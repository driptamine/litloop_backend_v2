import logging
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from albums.models import Album
from litloop_project.serializers_no_drf import (
    serialize_album, paginate_queryset, get_paginated_response
)
from litloop_project.utils.spotipy_util import get_spotify_client

logger = logging.getLogger(__name__)

class SpotifyBaseView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self.sp = get_spotify_client()
        except Exception as e:
            logger.error(f"Failed to initialize Spotify client: {e}")
            self.sp = None

    def handle_spotify_error(self, e):
        logger.error(f"Spotify API Error: {e}")
        return JsonResponse(
            {"error": "Failed to connect to Spotify. Please check credentials and connectivity."},
            status=503
        )

class FeedView(SpotifyBaseView):
    def get(self, request, *args, **kwargs):
        if not self.sp:
            return JsonResponse({"error": "Spotify client not configured"}, status=503)

        try:
            feed_info = self.sp.new_releases(country="US", limit=50)
            
            # Sync albums in DB
            for album_data in feed_info['albums']['items']:
                try:
                    album_uri = album_data['id']
                    album_info = self.sp.album(album_uri)
                    Album.objects.create_album(**album_info)
                except Exception as inner_e:
                    logger.warning(f"Failed to sync album {album_data.get('id')}: {inner_e}")

            queryset = Album.objects.all().order_by('-created_at')
            items, paginator = paginate_queryset(queryset, request, page_size=10)
            response_data = get_paginated_response(items, paginator, serialize_album, request)
            return JsonResponse(response_data)
            
        except Exception as e:
            return self.handle_spotify_error(e)

class SearchAlbumView(SpotifyBaseView):
    def get(self, request):
        if not self.sp:
            return JsonResponse({"error": "Spotify client not configured"}, status=503)

        term = request.GET.get('q', None)
        if not term:
            return JsonResponse({"error": "Query parameter 'q' is required"}, status=400)

        try:
            search_result = self.sp.search(term, limit=50, type='album')
            return JsonResponse(search_result.get('albums', {}))
        except Exception as e:
            return self.handle_spotify_error(e)

class AlbumDetailView(SpotifyBaseView):
    def get(self, request, album_uri):
        if not self.sp:
            return JsonResponse({"error": "Spotify client not configured"}, status=503)

        try:
            album_info = self.sp.album(album_uri)
            # Sync with DB
            Album.objects.create_album(**album_info)
            
            album = get_object_or_404(Album, album_uri=album_uri)
            return JsonResponse(serialize_album(album, request))
        except Exception as e:
            return self.handle_spotify_error(e)

class AlbumDetailedView(SpotifyBaseView):
    def get(self, request, album_uri):
        if not self.sp:
            return JsonResponse({"error": "Spotify client not configured"}, status=503)

        try:
            album_info = self.sp.album(album_uri, market="KZ")
            return JsonResponse(album_info)
        except Exception as e:
            return self.handle_spotify_error(e)
