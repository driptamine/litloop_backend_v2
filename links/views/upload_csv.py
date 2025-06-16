import csv
from datetime import datetime
from django.http import JsonResponse
from django.utils.timezone import make_aware
from django.views.decorators.csrf import csrf_exempt

from links.models import Link, Hashtag, LinkTag

@csrf_exempt  # only if you’re testing without CSRF token, better to handle CSRF properly in prod
def upload_csv_api(request):
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

    imported_count = 0
    errors = []

    for i, row in enumerate(reader, start=1):
        try:
            title = row.get('title') or None
            url = row['url']
            time_added = int(row['time_added'])
            dt_added = make_aware(datetime.fromtimestamp(time_added))
            status = row.get('status', 'unread')
            tags_raw = row.get('tags', '')

            link = Link.objects.create(
                title=title,
                url=url,
                status=status,
                time_added=dt_added,
            )

            tags = [t.strip() for t in tags_raw.split('|') if t.strip()]
            for tag_name in tags:
                hashtag, _ = Hashtag.objects.get_or_create(name=tag_name)
                LinkTag.objects.create(link=link, hashtag=hashtag)

            imported_count += 1
        except Exception as e:
            errors.append({'row': i, 'error': str(e)})

    return JsonResponse({
        'imported': imported_count,
        'errors': errors,
    })
