import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from users.auth_utils import jwt_required
from movies.models import WatchlistItem


@csrf_exempt
@jwt_required
def ammy_shuffle_watchlist(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'GET required'}, status=400)

    user = request.user

    # Get all watchlist items for this user
    watchlist_items = (
        WatchlistItem.objects
        .filter(user=user)
        .select_related('movie')
    )

    # Convert to list so we can shuffle in Python
    watchlist_list = list(watchlist_items)
    random.shuffle(watchlist_list)

    # Optional: limit to N random items
    limit = int(request.GET.get('limit', len(watchlist_list)))
    watchlist_list = watchlist_list[:limit]

    # Serialize to JSON
    results = []
    for item in watchlist_list:
        movie = item.movie
        results.append({
            'imdb_id': movie.imdb_id,
            'title': movie.title,
            'your_rating': item.user_rating,
            'date_rated': item.date_rated.isoformat() if item.date_rated else None,
            'imdb_rating': movie.imdb_rating,
            'year': movie.year,
            'genres': movie.genres,
            'url': movie.url,
        })

    return JsonResponse({
        'count': len(results),
        'results': results
    })
