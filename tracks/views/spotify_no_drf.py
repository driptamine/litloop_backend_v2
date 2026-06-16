import logging
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from tracks.models import Track
from litloop_project.serializers_no_drf import (
    serialize_track, paginate_queryset, get_paginated_response
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

class SearchTrackView(SpotifyBaseView):
    def get(self, request):
        if not self.sp:
            return JsonResponse({"error": "Spotify client not configured"}, status=503)

        term = request.GET.get('q', None)
        if not term:
            return JsonResponse({"error": "Query parameter 'q' is required"}, status=400)

        try:
            search_result = self.sp.search(term, limit=10, type='track')
            return JsonResponse(search_result.get('tracks', {}))
        except Exception as e:
            return self.handle_spotify_error(e)

class TrackDetailView(SpotifyBaseView):
    def get(self, request, track_uri):
        if not self.sp:
            return JsonResponse({"error": "Spotify client not configured"}, status=503)

        try:
            track_info = self.sp.track(track_uri)
            return JsonResponse(track_info)
        except Exception as e:
            return self.handle_spotify_error(e)

class TrackGetOrCreateView(SpotifyBaseView):
    def get(self, request, track_uri):
        if not self.sp:
            return JsonResponse({"error": "Spotify client not configured"}, status=503)

        try:
            track_data = self.sp.track(track_uri)
            
            from artists.models import Artist
            from albums.models import Album
            
            album_uri = track_data['album']['id']
            album_data = self.sp.album(album_uri)
            
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

            return JsonResponse(serialize_track(track, request))
        except Exception as e:
            return self.handle_spotify_error(e)
