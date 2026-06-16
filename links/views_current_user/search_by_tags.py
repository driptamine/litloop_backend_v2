from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Link


@login_required
def search_user_links_by_tag(request):
    user = request.user
    query = request.GET.get('q', '').strip()

    # Start with the current user's links
    links = Link.objects.filter(user=user).select_related('user').prefetch_related('hashtags')

    # If there's a search query, filter by title, url, or hashtag name
    if query:
        links = links.filter(
            # Q(title__icontains=query) |
            # Q(url__icontains=query) |
            Q(hashtags__name__icontains=query)
        ).distinct()

    # Serialize the links to JSON
    data = []
    for link in links:
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

    return JsonResponse(data, safe=False)
