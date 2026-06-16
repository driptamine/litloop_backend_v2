from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
import logging

from tracks.models import Track
from tracks.serializers import TrackSerializer
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

class SearchTrackAPIView(SpotifyBaseView):
    def get(self, request):
        if not self.sp:
            return Response({"error": "Spotify client not configured"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        term = request.query_params.get('q', None)
        if not term:
            return Response({"error": "Query parameter 'q' is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            search_result = self.sp.search(term, limit=10, type='track')
            return Response(search_result.get('tracks'))
        except Exception as e:
            return self.handle_spotify_error(e)

class TrackDetailAPIView(SpotifyBaseView):
    def get(self, request, track_uri):
        if not self.sp:
            return Response({"error": "Spotify client not configured"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            track_info = self.sp.track(track_uri)
            return Response(track_info)
        except Exception as e:
            return self.handle_spotify_error(e)

class TrackGetOrCreateAPIView(SpotifyBaseView):
    def get(self, request, track_uri):
        if not self.sp:
            return Response({"error": "Spotify client not configured"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            track_data = self.sp.track(track_uri)
            
            # Since managers seem broken/incorrectly used in original code,
            # we should be careful. Original code used Track.create which likely failed.
            # For now, we'll try to use a safer approach or just return the data 
            # if DB sync is not critical, but the user likely wants it in DB.
            
            # If I fix TrackManager, I can use Track.objects.create_track
            # But let's first see if we can just get or create it simply.
            
            from artists.models import Artist
            from albums.models import Album
            
            album_uri = track_data['album']['id']
            album_data = self.sp.album(album_uri)
            
            # Using get_or_create directly as a fallback
            album, _ = Album.objects.get_or_create(
                album_uri=album_uri,
                defaults={'name': album_data['name']}
            )
            
            track, _ = Track.objects.get_or_create(
                track_uri=track_uri,
                defaults={
                    'name': track_data['name'],
                    'album': album,
                    'track_number': track_data['track_number']
                }
            )
            
            for artist_data in track_data['artists']:
                artist, _ = Artist.objects.get_or_create(
                    artist_uri=artist_data['id'],
                    defaults={'name': artist_data['name']}
                )
                track.artists.add(artist)

            serializer = TrackSerializer(track, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            return self.handle_spotify_error(e)
