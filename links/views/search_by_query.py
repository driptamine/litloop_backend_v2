import json
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db.models import Q

from links.models import Link

@require_GET
def search_by_query(request):
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        # links = Link.objects.filter(hashtags__name__icontains=query).distinct()


        links = Link.objects.filter(
            Q(title__icontains=query) |
            Q(url__icontains=query) 
            # Q(hashtags__name__icontains=query)
        ).distinct()


        for link in links:
            results.append({
                'id': link.id,
                'url': link.url,
                'hashtags': [h.name for h in link.hashtags.all()],
                'user_id': link.user.id if link.user else None,
            })

    return JsonResponse({
        'query': query,
        'results': results
    })
