import logging
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from artists.models import Artist
from litloop_project.serializers_no_drf import (
    serialize_artist, serialize_album, paginate_queryset, get_paginated_response
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

class SearchArtistView(SpotifyBaseView):
    def get(self, request):
        if not self.sp:
            return JsonResponse({"error": "Spotify client not configured"}, status=503)

        term = request.GET.get('q', None)
        if not term:
            return JsonResponse({"error": "Query parameter 'q' is required"}, status=400)

        try:
            search_result = self.sp.search(term, limit=10, type='artist')
            return JsonResponse(search_result.get('artists', {}))
        except Exception as e:
            return self.handle_spotify_error(e)

class ArtistDetailView(SpotifyBaseView):
    def get(self, request, artist_uri):
        if not self.sp:
            return JsonResponse({"error": "Spotify client not configured"}, status=503)

        try:
            from albums.models import Album
            
            artist_info = self.sp.artist(artist_uri)
            artist_albums_info = self.sp.artist_albums(artist_uri, limit=10)

            # Sync artist
            artist, _ = Artist.objects.get_or_create(
                artist_uri=artist_uri,
                defaults={'name': artist_info['name']}
            )

            # Sync albums
            for album_data in artist_albums_info['items']:
                try:
                    album_uri = album_data['id']
                    album_full_info = self.sp.album(album_uri)
                    if hasattr(Album.objects, 'create_album'):
                        Album.objects.create_album(**album_full_info)
                except Exception as inner_e:
                    logger.warning(f"Failed to sync album {album_data.get('id')}: {inner_e}")

            artist = get_object_or_404(Artist, artist_uri=artist_uri)
            return JsonResponse(serialize_artist(artist, request))
        except Exception as e:
            return self.handle_spotify_error(e)

class ArtistAPIView(SpotifyBaseView):
    def get(self, request, artist_uri):
        if not self.sp:
            return JsonResponse({"error": "Spotify client not configured"}, status=503)

        try:
            artist_info = self.sp.artist(artist_uri)
            return JsonResponse(artist_info)
        except Exception as e:
            return self.handle_spotify_error(e)

class ArtistAlbumsView(SpotifyBaseView):
    def get(self, request, artist_uri):
        if not self.sp:
            return JsonResponse({"error": "Spotify client not configured"}, status=503)

        try:
            from albums.models import Album
            artist_albums_info = self.sp.artist_albums(artist_uri, limit=10)

            for album_data in artist_albums_info['items']:
                try:
                    album_uri = album_data['id']
                    album_full_info = self.sp.album(album_uri)
                    if hasattr(Album.objects, 'create_album'):
                        Album.objects.create_album(**album_full_info)
                except Exception as inner_e:
                    logger.warning(f"Failed to sync album {album_data.get('id')}: {inner_e}")

            artist = get_object_or_404(Artist, artist_uri=artist_uri)
            return JsonResponse(serialize_artist(artist, request))
        except Exception as e:
            return self.handle_spotify_error(e)

class ArtistRelatedArtistsDetailView(SpotifyBaseView):
    def get(self, request, artist_uri):
        if not self.sp:
            return JsonResponse({"error": "Spotify client not configured"}, status=503)

        try:
            artist_related_artists_info = self.sp.artist_related_artists(artist_uri)
            return JsonResponse(artist_related_artists_info)
        except Exception as e:
            return self.handle_spotify_error(e)
