from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveAPIView,
    ListAPIView,
    CreateAPIView
)
from django.http import HttpResponse

from posts.models import Post
from users.models import User

from movies.tasks import increment_view, create_or_update_movie
from movies.models import Movie
from movies.serializers import MovieSerializer

class ViewsUP(APIView):
    def post(self, request):
        user_id = request.POST['user_id']
        tmdb_id = request.POST['tmdb_id']

        # Trigger the asynchronous task to process the like process_view.delay(user.id, post.id)
        result = increment_view.delay(user_id, tmdb_id)
        # return Response(status=status.HTTP_202_ACCEPTED)
        return HttpResponse(f'View Accepted {result.id}')


class AddMovie(APIView):
    def post(self, request):

        # Trigger the asynchronous task to create movie
        result = create_or_update_movie.delay()
        # return Response(status=status.HTTP_202_ACCEPTED)
        return HttpResponse(f'View Accepted {result.id}')

# class FeedMovies(APIView):
#
#     def get(self, request):
#         movies = Movie.objects.all()
#
#         return Response(movies)

class FeedMovies(ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
