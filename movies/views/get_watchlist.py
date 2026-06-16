from django.core.paginator import Paginator, EmptyPage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model

from users.auth_utils import jwt_required
from movies.models import WatchlistItem


@csrf_exempt
@jwt_required
def get_watchlist(request, user_id):
    if request.method != 'GET':
        return JsonResponse({'error': 'GET required'}, status=400)

    # user = request.user
    user = get_object_or_404(User, id=user_id)

    watchlist_qs = (
        WatchlistItem.objects
        .filter(user=user)
        .select_related('movie')
        .order_by('-date_rated')  # or whatever default order you want
    )

    # Get pagination params from query string
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))

    paginator = Paginator(watchlist_qs, page_size)

    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        return JsonResponse({
            'error': 'Page out of range'
        }, status=404)

    results = []
    for item in page_obj:
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

    response = {
        'count': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page,
        'page_size': page_size,
        'results': results,
    }

    return JsonResponse(response)
