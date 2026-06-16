from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
import logging

from albums.models import Album
from albums.serializers import AlbumsSerializer
from litloop_project.utils.spotipy_util import get_spotify_client

logger = logging.getLogger(__name__)

class SpotifyBaseView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self.sp = get_spotify_client()
        except Exception as e:
            logger.error(f"Failed to initialize Spotify client: {e}")
            self.sp = None

    def handle_spotify_error(self, e):
        logger.error(f"Spotify API Error: {e}")
        return Response(
            {"error": "Failed to connect to Spotify. Please check credentials and connectivity."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

class FeedAPIView(SpotifyBaseView, PageNumberPagination):
    serializer_class = AlbumsSerializer
    page_size = 10

    def get(self, request, *args, **kwargs):
        if not self.sp:
            return Response({"error": "Spotify client not configured"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            feed_info = self.sp.new_releases(country="US", limit=50)
            
            # Optimization: Create/Update albums in DB
            for album_data in feed_info['albums']['items']:
                try:
                    album_uri = album_data['id']
                    album_info = self.sp.album(album_uri)
                    Album.objects.create_album(**album_info)
                except Exception as inner_e:
                    logger.warning(f"Failed to sync album {album_data.get('id')}: {inner_e}")

            queryset = Album.objects.all().order_by('-created_at')
            page = self.paginate_queryset(queryset, request)
            if page is not None:
                serializer = AlbumsSerializer(page, many=True, context={'request': request})
                return self.get_paginated_response(serializer.data)

            serializer = AlbumsSerializer(queryset, many=True, context={'request': request})
            return Response(serializer.data)
            
        except Exception as e:
            return self.handle_spotify_error(e)

class SearchAlbumAPIView(SpotifyBaseView):
    def get(self, request):
        if not self.sp:
            return Response({"error": "Spotify client not configured"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        term = request.query_params.get('q', None)
        if not term:
            return Response({"error": "Query parameter 'q' is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            search_result = self.sp.search(term, limit=50, type='album')
            return Response(search_result.get('albums'))
        except Exception as e:
            return self.handle_spotify_error(e)

class AlbumDetailAPIView(SpotifyBaseView):
    def get(self, request, album_uri):
        if not self.sp:
            return Response({"error": "Spotify client not configured"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            album_info = self.sp.album(album_uri)
            # Sync with DB
            Album.objects.create_album(**album_info)
            
            snippet = get_object_or_404(Album, album_uri=album_uri)
            serializer = AlbumsSerializer(snippet, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            return self.handle_spotify_error(e)

class AlbumDetailedAPIView(SpotifyBaseView):
    def get(self, request, album_uri):
        if not self.sp:
            return Response({"error": "Spotify client not configured"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            album_info = self.sp.album(album_uri, market="KZ")
            return Response(album_info)
        except Exception as e:
            return self.handle_spotify_error(e)
