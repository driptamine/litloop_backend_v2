from django.views.decorators.http import require_GET
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from links.models import Link

@require_GET
def all_links_api(request):
    links = Link.objects.all().distinct()

    # Get pagination params from query string with defaults
    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    try:
        page = int(page)
        page_size = int(page_size)
    except ValueError:
        return JsonResponse({'error': 'Invalid page or page_size'}, status=400)

    paginator = Paginator(links, page_size)

    try:
        links_page = paginator.page(page)
    except PageNotAnInteger:
        links_page = paginator.page(1)
    except EmptyPage:
        links_page = paginator.page(paginator.num_pages)

    results = []
    for link in links_page:
        results.append({
            'id': link.id,
            'url': link.url,
            'hashtags': [h.name for h in link.hashtags.all()],
            'user_id': link.user.id if link.user else None,
            'created_at': link.created_at.isoformat() if link.created_at else None,
            'updated_at': link.updated_at.isoformat() if link.updated_at else None,
            'time_added': link.time_added.isoformat() if link.time_added else None,
        })

    return JsonResponse({
        'results': results,
        'page': page,
        'page_size': page_size,
        'total_pages': paginator.num_pages,
        'total_items': paginator.count,
    })
