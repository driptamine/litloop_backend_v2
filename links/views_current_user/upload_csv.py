import csv
from datetime import datetime
from django.http import JsonResponse
from django.utils.timezone import make_aware
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction

from links.models import Link, Hashtag, LinkTag


@login_required
def upload_csv_bulk(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file uploaded'}, status=400)

    csv_file = request.FILES['file']

    try:
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
    except Exception as e:
        return JsonResponse({'error': f'Invalid CSV file: {str(e)}'}, status=400)

    links_to_create = []
    link_tags_to_create = []
    hashtag_cache = {}  # name -> Hashtag instance

    errors = []
    imported_count = 0

    # First pass: parse rows, prepare Link objects
    for i, row in enumerate(reader, start=1):
        try:
            title = (row.get('title') or '')[:255]
            url = (row['url'])[:500]
            time_added = int(row['time_added'])
            dt_added = make_aware(datetime.fromtimestamp(time_added))
            status = (row.get('status') or 'unread')[:50]
            tags_raw = row.get('tags', '')

            link = Link(
                user=request.user,  # ✅ assign current user
                title=title,
                url=url,
                status=status,
                time_added=dt_added,
            )
            # Temporarily store tags with the Link for later LinkTag creation
            link._tags_raw = [t.strip() for t in tags_raw.split('|') if t.strip()]

            links_to_create.append(link)
        except Exception as e:
            errors.append({'row': i, 'error': str(e)})

    with transaction.atomic():
        # Bulk create Link objects
        created_links = Link.objects.bulk_create(links_to_create, batch_size=1000)

        # Collect all unique tag names from all links
        all_tags = set()
        for link in created_links:
            all_tags.update(link._tags_raw)

        # Get existing hashtags from DB
        existing_hashtags = Hashtag.objects.filter(name__in=all_tags)
        for ht in existing_hashtags:
            hashtag_cache[ht.name] = ht

        # Create missing hashtags
        new_hashtags = [Hashtag(name=name) for name in all_tags if name not in hashtag_cache]
        created_hashtags = Hashtag.objects.bulk_create(new_hashtags, batch_size=1000)
        for ht in created_hashtags:
            hashtag_cache[ht.name] = ht

        # Now prepare LinkTag objects to bulk create
        for link in created_links:
            for tag_name in link._tags_raw:
                hashtag = hashtag_cache.get(tag_name)
                if hashtag:
                    link_tags_to_create.append(LinkTag(link=link, hashtag=hashtag))

        LinkTag.objects.bulk_create(link_tags_to_create, batch_size=1000)

        imported_count = len(created_links)

    return JsonResponse({
        'imported': imported_count,
        'errors': errors,
    })
