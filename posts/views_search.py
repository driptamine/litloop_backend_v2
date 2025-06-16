
from django.http import JsonResponse
from django.conf import settings
from django.views import View

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

SPOTIPY_CLIENT_ID = settings.SPOTIPY_CLIENT_ID
SPOTIPY_CLIENT_SECRET = settings.SPOTIPY_CLIENT_SECRET

print(f"DEBUG: SPOTIPY_CLIENT_ID = '{SPOTIPY_CLIENT_ID}'")
print(f"DEBUG: SPOTIPY_CLIENT_SECRET = '{SPOTIPY_CLIENT_SECRET}'")


from litloop_project.utils.spotipy_util import get_spotify_client

sp = get_spotify_client()

class SearchArtistView(View):
    def get(self, request):
        term = request.GET.get('q')
        offset = request.GET.get('offset', 0)

        if not term:
            return JsonResponse({'error': 'Missing query parameter: q'}, status=400)

        search_result = sp.search(term, offset=int(offset), limit=50, type='artist')
        return JsonResponse(search_result.get('artists', {}), safe=False)


class SearchTrackView(View):
    def get(self, request):
        term = request.GET.get('q')
        offset = request.GET.get('offset', 0)

        if not term:
            return JsonResponse({'error': 'Missing query parameter: q'}, status=400)

        search_result = sp.search(term, offset=int(offset), limit=50, type='track', market="US")
        return JsonResponse(search_result.get('tracks', {}), safe=False)


class SearchAlbumView(View):
    def get(self, request):
        term = request.GET.get('q')
        offset = request.GET.get('offset', 0)

        if not term:
            return JsonResponse({'error': 'Missing query parameter: q'}, status=400)

        search_result = sp.search(term, offset=int(offset), limit=50, type='album')
        return JsonResponse(search_result.get('albums', {}), safe=False)
