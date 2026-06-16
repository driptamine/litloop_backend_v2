from django.views.decorators.http import require_GET
from django.http import JsonResponse
from django.core.paginator import Paginator
from links.models import Link

@require_GET
def all_links_api(request):
    links = Link.objects.all().distinct().order_by('-created_at')  # Sort by recent first

    # Pagination params with defaults and safe conversion
    try:
        page = max(int(request.GET.get('page', 1)), 1)
        page_size = min(max(int(request.GET.get('page_size', 10)), 1), 100)  # limit page_size max 100 for safety
    except ValueError:
        return JsonResponse({'error': 'Invalid page or page_size'}, status=400)

    paginator = Paginator(links, page_size)

    try:
        links_page = paginator.page(page)
    except Exception:
        # Return last page if out of range or invalid
        links_page = paginator.page(paginator.num_pages)

    results = [
        {
            'id': link.id,
            'url': link.url,
            'hashtags': list(link.hashtags.values_list('name', flat=True)),
            'user_id': getattr(link.user, 'id', None),
            'created_at': link.created_at.isoformat() if link.created_at else None,
            'updated_at': link.updated_at.isoformat() if link.updated_at else None,
            'time_added': link.time_added.isoformat() if link.time_added else None,
        }
        for link in links_page
    ]

    return JsonResponse({
        'results': results,
        'page': page,
        'page_size': page_size,
        'total_pages': paginator.num_pages,
        'total_items': paginator.count,
    })
