import os


# ─── LIKES MODELS ──────────────────────────────────────────────────────────
LIKES_MODELS = {
    "posts.Post":   {'serializer': 'posts.serializers.PostSerializer'},
    "albums.Album": {'serializer': 'albums.serializers.AlbumsSerializer'},
    "tracks.Track": {'serializer': 'tracks.serializers.TrackSerializer'},
}

# ─── MISC ──────────────────────────────────────────────────────────────────
FRIENDLY_TOKEN_LEN = 11
FRIENDLY_COMMENT_TOKEN_LEN = 26
MASK_IPS_FOR_ACTIONS = True
RUNNING_STATE_STALE = 60 * 60 * 2
MEDIA_IS_REVIEWED = True
PORTAL_WORKFLOW = "private"
LOCAL_INSTALL = False
GLOBAL_LOGIN_REQUIRED = False
POST_UPLOAD_AUTHOR_MESSAGE_UNLISTED_NO_COMMENTARY = ""
CANNOT_ADD_MEDIA_MESSAGE = ""
TMDB_API_KEY = os.environ.get('TMDB_API_KEY', 'bceb6c0fefae8ee5a3cf9762ec780d63')
