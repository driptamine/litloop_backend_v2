from django.conf import settings

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.cache_handler import CacheHandler

SPOTIPY_CLIENT_ID = settings.SPOTIPY_CLIENT_ID
SPOTIPY_CLIENT_SECRET = settings.SPOTIPY_CLIENT_SECRET

class NoCacheHandler(CacheHandler):
    def get_cached_token(self):
        return None
    def save_token_to_cache(self, token_info):
        pass

def get_spotify_client():
    return spotipy.Spotify(
        client_credentials_manager=SpotifyClientCredentials(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            cache_handler=NoCacheHandler()
        )
    )
