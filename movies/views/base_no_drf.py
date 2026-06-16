from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from movies.tasks import increment_view, create_or_update_movie
from movies.models import Movie

def serialize_movie(movie, request=None):
    return {
        'id': movie.id,
        'title': movie.title,
        'description': movie.description,
        'tmdb_id': getattr(movie, 'tmdb_id', None),
        # Add other fields as needed based on the model
    }

@csrf_exempt
def views_up_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    
    user_id = request.POST.get('user_id')
    tmdb_id = request.POST.get('tmdb_id')

    if not user_id or not tmdb_id:
        return JsonResponse({'error': 'user_id and tmdb_id are required'}, status=400)

    result = increment_view.delay(user_id, tmdb_id)
    return HttpResponse(f'View Accepted {result.id}')

@csrf_exempt
def add_movie_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
        
    result = create_or_update_movie.delay()
    return HttpResponse(f'View Accepted {result.id}')

def feed_movies_view(request):
    movies = Movie.objects.all()
    data = [serialize_movie(m, request) for m in movies]
    return JsonResponse(data, safe=False)
