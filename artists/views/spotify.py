from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
import logging

from artists.models import Artist
from artists.serializers import ArtistSerializer
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

class SearchArtistAPIView(SpotifyBaseView):
    def get(self, request):
        if not self.sp:
            return Response({"error": "Spotify client not configured"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        term = request.query_params.get('q', None)
        if not term:
            return Response({"error": "Query parameter 'q' is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            search_result = self.sp.search(term, limit=10, type='artist')
            return Response(search_result.get('artists'))
        except Exception as e:
            return self.handle_spotify_error(e)

class ArtistDetailAPIView(SpotifyBaseView):
    def get(self, request, artist_uri):
        if not self.sp:
            return Response({"error": "Spotify client not configured"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

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
                    # Using the Album manager method if it exists
                    if hasattr(Album.objects, 'create_album'):
                        Album.objects.create_album(**album_full_info)
                    else:
                        Album.objects.get_or_create(
                            album_uri=album_uri,
                            defaults={'name': album_full_info['name']}
                        )
                except Exception as inner_e:
                    logger.warning(f"Failed to sync album {album_data.get('id')}: {inner_e}")

            snippet = get_object_or_404(Artist, artist_uri=artist_uri)
            serializer = ArtistSerializer(snippet, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            return self.handle_spotify_error(e)

class ArtistAPIView(SpotifyBaseView):
    def get(self, request, artist_uri):
        if not self.sp:
            return Response({"error": "Spotify client not configured"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            artist_info = self.sp.artist(artist_uri)
            return Response(artist_info)
        except Exception as e:
            return self.handle_spotify_error(e)

class ArtistAlbumsAPIView(SpotifyBaseView):
    def get(self, request, artist_uri):
        if not self.sp:
            return Response({"error": "Spotify client not configured"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            from albums.models import Album
            artist_albums_info = self.sp.artist_albums(artist_uri, limit=10)

            for album_data in artist_albums_info['items']:
                try:
                    album_uri = album_data['id']
                    album_full_info = self.sp.album(album_uri)
                    if hasattr(Album.objects, 'create_album'):
                        Album.objects.create_album(**album_full_info)
                    else:
                        Album.objects.get_or_create(
                            album_uri=album_uri,
                            defaults={'name': album_full_info['name']}
                        )
                except Exception as inner_e:
                    logger.warning(f"Failed to sync album {album_data.get('id')}: {inner_e}")

            snippet = get_object_or_404(Artist, artist_uri=artist_uri)
            serializer = ArtistSerializer(snippet, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            return self.handle_spotify_error(e)

class ArtistAlbumsOldAPIView(SpotifyBaseView):
    def get(self, request, artist_uri):
        if not self.sp:
            return Response({"error": "Spotify client not configured"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            artist_albums_info = self.sp.artist_albums(artist_uri, limit=50, country="US")
            return Response(artist_albums_info)
        except Exception as e:
            return self.handle_spotify_error(e)

class ArtistRelatedArtistsDetailAPIView(SpotifyBaseView):
    def get(self, request, artist_uri):
        if not self.sp:
            return Response({"error": "Spotify client not configured"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            artist_related_artists_info = self.sp.artist_related_artists(artist_uri)
            return Response(artist_related_artists_info)
        except Exception as e:
            return self.handle_spotify_error(e)
