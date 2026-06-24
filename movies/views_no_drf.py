from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import json

from movies.models import Movie
from movies.tasks import increment_view, create_or_update_movie, scrape_tmdb_movie
from movies.utils import tmdb as tmdb_utils
from litloop_project.serializers_no_drf import (
    serialize_movie, paginate_queryset, get_paginated_response
)
from users.auth_utils import jwt_required_testable
from movies import redis_utils

@csrf_exempt
def views_up_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    
    user_id = request.POST.get('user_id')
    tmdb_id = request.POST.get('tmdb_id')

    if not user_id or not tmdb_id:
        return JsonResponse({'error': 'user_id and tmdb_id are required'}, status=400)

    # Trigger the asynchronous task
    result = increment_view.delay(user_id, tmdb_id)
    return HttpResponse(f'View Accepted {result.id}')

@csrf_exempt
def add_movie_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    
    # Trigger the asynchronous task to create movie
    result = create_or_update_movie.delay()
    return HttpResponse(f'View Accepted {result.id}')

def feed_movies_view(request):
    page = request.GET.get('page', 1)

    data = tmdb_utils.get_popular(page=page)
    if not data:
        return JsonResponse({'error': 'Failed to fetch popular movies'}, status=502)

    for item in data.get('results', []):
        tmdb_id = item.get('id')
        if not tmdb_id:
            continue

        poster_path = item.get('poster_path')
        backdrop_path = item.get('backdrop_path')

        movie, created = Movie.objects.get_or_create(
            tmdb_id=tmdb_id,
            defaults={
                'title': item.get('title', ''),
                'description': item.get('overview', ''),
                'poster': f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else '',
                'movie_file': f"https://image.tmdb.org/t/p/w1280{backdrop_path}" if backdrop_path else '',
            }
        )

        item['db_id'] = movie.id

        if created or not movie.imdb_id:
            scrape_tmdb_movie.delay(tmdb_id)

    return JsonResponse(data)


def list_movies_view(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET allowed'}, status=405)

    queryset = Movie.objects.all()

    search = request.GET.get('search')
    if search:
        queryset = queryset.filter(title__icontains=search)

    tmdb_ids = request.GET.get('tmdb_ids')
    if tmdb_ids:
        ids = [int(x) for x in tmdb_ids.split(',') if x.strip().isdigit()]
        if ids:
            queryset = queryset.filter(tmdb_id__in=ids)

    items, paginator = paginate_queryset(queryset, request, page_size=20)
    response_data = get_paginated_response(items, paginator, serialize_movie, request)
    return JsonResponse(response_data)


@csrf_exempt
@jwt_required_testable
def record_movie_impressions(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    movie_ids = data.get('movie_ids', [])
    if not movie_ids or not isinstance(movie_ids, list):
        return JsonResponse({'error': 'movie_ids must be a non-empty list'}, status=400)

    for movie_id in movie_ids:
        redis_utils.record_impression(movie_id)
    return JsonResponse({'status': 'ok', 'enqueued': len(movie_ids)})


@csrf_exempt
@jwt_required_testable
def movie_like_view(request, tmdb_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        movie = Movie.objects.get(tmdb_id=tmdb_id)
    except Movie.DoesNotExist:
        return JsonResponse({'error': 'Movie not found'}, status=404)

    user = request.user
    movie_db_id = movie.id

    if redis_utils.is_liked(movie_db_id, user.id):
        redis_utils.unlike_movie(movie_db_id, user.id)
        liked = False
    else:
        redis_utils.like_movie(movie_db_id, user.id)
        liked = True

    count = redis_utils.get_likes_count(movie_db_id)
    if count is None:
        count = movie.likes_count

    return JsonResponse({
        'liked': liked,
        'likes_count': count,
    })
