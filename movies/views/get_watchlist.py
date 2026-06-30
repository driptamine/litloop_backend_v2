from django.core.paginator import Paginator, EmptyPage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from users.auth_utils import jwt_required
from movies.models import WatchlistItem, ImdbMovieRating, ImdbMovie


@csrf_exempt
@jwt_required
def get_watchlist(request, user_id):
    if request.method != 'GET':
        return JsonResponse({'error': 'GET required'}, status=400)

    user = get_object_or_404(User, id=user_id)

    watchlist_qs = (
        WatchlistItem.objects
        .filter(user=user)
        .select_related('movie')
        .order_by('-date_rated')
    )

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


def user_watchlist_by_username(request, username):
    if request.method != 'GET':
        return JsonResponse({'error': 'GET required'}, status=400)

    User = get_user_model()
    user = get_object_or_404(User, username=username)

    watchlist_qs = (
        WatchlistItem.objects
        .filter(user=user)
        .select_related('movie')
        .order_by('-date_rated')
    )

    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))

    paginator = Paginator(watchlist_qs, page_size)

    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        return JsonResponse({'error': 'Page out of range'}, status=404)

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

    return JsonResponse({
        'username': username,
        'count': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page,
        'page_size': page_size,
        'results': results,
    })


def user_ratings_by_username(request, username):
    if request.method != 'GET':
        return JsonResponse({'error': 'GET required'}, status=400)

    User = get_user_model()
    user = get_object_or_404(User, username=username)

    ratings_qs = (
        ImdbMovieRating.objects
        .filter(user=user)
        .select_related('imdb_movie')
        .order_by('-date_rated', '-updated_at')
    )

    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))

    paginator = Paginator(ratings_qs, page_size)

    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        return JsonResponse({'error': 'Page out of range'}, status=404)

    results = []
    for item in page_obj:
        movie = item.imdb_movie
        results.append({
            'imdb_id': movie.imdb_id,
            'title': movie.title,
            'rating': item.rating,
            'date_rated': item.date_rated.isoformat() if item.date_rated else None,
            'created_at': item.created_at.isoformat() if item.created_at else None,
            'updated_at': item.updated_at.isoformat() if item.updated_at else None,
            'imdb_rating': movie.imdb_rating,
            'year': movie.year,
            'genres': movie.genres,
            'url': movie.url,
            'title_type': movie.title_type,
            'directors': movie.directors,
        })

    return JsonResponse({
        'username': username,
        'count': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page,
        'page_size': page_size,
        'results': results,
    })
