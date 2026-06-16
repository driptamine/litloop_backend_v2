from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

from movies.models import Movie
from movies.tasks import increment_view, create_or_update_movie
from litloop_project.serializers_no_drf import (
    serialize_movie, paginate_queryset, get_paginated_response
)

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
    queryset = Movie.objects.all()
    items, paginator = paginate_queryset(queryset, request, page_size=10)
    response_data = get_paginated_response(items, paginator, serialize_movie, request)
    return JsonResponse(response_data)
