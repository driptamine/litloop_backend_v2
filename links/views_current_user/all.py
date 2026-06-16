from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Link


@login_required
def user_links_json(request):
    user = request.user

    # Get all links for this user
    links = Link.objects.filter(user=user).select_related('user').prefetch_related('hashtags')

    # Get page number & page size from query params
    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    try:
        page_size = int(page_size)
    except ValueError:
        page_size = 10

    paginator = Paginator(links, page_size)

    try:
        links_page = paginator.page(page)
    except PageNotAnInteger:
        links_page = paginator.page(1)
    except EmptyPage:
        links_page = paginator.page(paginator.num_pages)

    data = []
    for link in links_page:
        data.append({
            'id': link.id,
            'title': link.title,
            'url': link.url,
            'status': link.status,
            'created_at': link.created_at.isoformat(),
            'updated_at': link.updated_at.isoformat(),
            'time_added': link.time_added.isoformat() if link.time_added else None,
            'hashtags': [hashtag.name for hashtag in link.hashtags.all()],
        })

    response = {
        'count': paginator.count,
        'num_pages': paginator.num_pages,
        'current_page': links_page.number,
        'page_size': page_size,
        'results': data,
    }

    return JsonResponse(response)
