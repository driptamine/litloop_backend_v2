import os
import re
from pathlib import Path
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

# ─── DATABASE_URL SANITIZATION ────────────────────────────────────────────
# Handles channel_binding and Neon SNI requirements before DB config uses it
_db_url = os.environ.get('DATABASE_URL')
if _db_url:
    if 'channel_binding=' in _db_url:
        _db_url = re.sub(r'[?&]channel_binding=[^&]+', '', _db_url)
    if 'neon.tech' in _db_url and 'options=endpoint' not in _db_url:
        match = re.search(r'@([^.]+)', _db_url)
        if match:
            endpoint_id = match.group(1)
            separator = '&' if '?' in _db_url else '?'
            _db_url += f"{separator}options=endpoint%3D{endpoint_id}"
    os.environ['DATABASE_URL'] = _db_url

# ─── PATHS ─────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMP_DIRECTORY = "/tmp"
SITE_URL = "http://localhost:8000"

# ─── SECURITY ──────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv('SECRET_KEY', 'qcss(9#e6wch%rq2zk8i89d3y=h9-#gt@b@g=69zzj#q_pf!(k')
X_FRAME_OPTIONS = "ALLOWALL"
AUTH_USER_MODEL = 'users.User'
AUTHENTICATION_BACKENDS = [
    'users.backends.EmailOrUsernameBackend',
    'django.contrib.auth.backends.ModelBackend',
]

if os.environ.get('ENVIRONMENT') == 'development':
    DEBUG = True
    ALLOWED_HOSTS = ['*']
else:
    DEBUG = False
    ALLOWED_HOSTS = ['*', 'litloop.netlify.app', 'litloop.duckdns.org']

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── APPLICATION ───────────────────────────────────────────────────────────
LOCAL_APPS = [
    'albums', 'artists', 'auth_cookie', 'comments', 'images',
    'chats', 'jobs', 'links', 'movies', 'notes', 'notifications',
    'photos', 'playlists', 'posts', 'queries', 'suggestions',
    'todos', 'tracks', 'users', 'videos', 'views', 'websites', 'memes',
]

THIRD_PARTY_APPS = [
    'channels', 'corsheaders', 'django_extensions', 'mptt', 'django_celery_beat',
]

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    *THIRD_PARTY_APPS,
    *LOCAL_APPS,
]

SITE_ID = 1
ROOT_URLCONF = 'litloop_project.urls'
WSGI_APPLICATION = 'litloop_project.wsgi.application'
ASGI_APPLICATION = 'litloop_project.asgi.application'
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

MIDDLEWARE = [
    'litloop_project.middleware.corss.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ["templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ─── I18N ──────────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ─── STATIC / MEDIA ────────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR + "/static/"
MEDIA_URL = "/uploaded_media/"
MEDIA_ROOT = BASE_DIR + "/uploaded_media/"
MEDIA_UPLOAD_DIR = "original/"
MEDIA_ENCODING_DIR = "encoded/"
THUMBNAIL_UPLOAD_DIR = f"{MEDIA_UPLOAD_DIR}/thumbnails/"
SUBTITLES_UPLOAD_DIR = f"{MEDIA_UPLOAD_DIR}/subtitles/"
HLS_DIR = os.path.join(MEDIA_ROOT, "hls/")
FILE_STORAGE = "django.core.files.storage.DefaultStorage"

# ─── LIKES MODELS ──────────────────────────────────────────────────────────
LIKES_MODELS = {
    "posts.Post":   {'serializer': 'posts.serializers.PostSerializer'},
    "albums.Album": {'serializer': 'albums.serializers.AlbumsSerializer'},
    "tracks.Track": {'serializer': 'tracks.serializers.TrackSerializer'},
}

# ─── AWS (Driptamine) ──────────────────────────────────────────────────────
AWS_REGION_DRIPTAMINE = 'eu-north-1'
AWS_ACCESS_KEY_DRIPTAMINE = os.environ.get('AWS_ACCESS_KEY_DRIPTAMINE')
AWS_SECRET_KEY_DRIPTAMINE = os.environ.get('AWS_SECRET_KEY_DRIPTAMINE')
AWS_STORAGE_BUCKET_NAME_DRIPTAMINE = os.environ.get('AWS_STORAGE_BUCKET_DRIPTAMINE', 'litloop_bucket_free')

# ─── AWS (Qalybay) ─────────────────────────────────────────────────────────
AWS_REGION_QALYBAY = 'eu-north-1'
AWS_ACCESS_KEY_QALYBAY = os.environ.get('AWS_ACCESS_KEY_QALYBAY')
AWS_SECRET_KEY_QALYBAY = os.environ.get('AWS_SECRET_KEY_QALYBAY')
AWS_STORAGE_BUCKET_NAME_QALYBAY = os.environ.get('AWS_STORAGE_BUCKET_NAME_QALYBAY')

# ─── S3 GENERIC ────────────────────────────────────────────────────────────
AWS_S3_USE_SSL = os.environ.get('AWS_S3_USE_SSL', 'false').lower() == 'true'
AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL')
AWS_QUERYSTRING_AUTH = False
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_CUSTOM_DOMAIN = os.environ.get('AWS_S3_CUSTOM_DOMAIN')
AWS_CLOUDFRONT_DOMAIN = 'https://xxxxx.cloudfront.net'
CLOUDFRONT_MEDIA_URL = 'https://{media-distribution-id}.cloudfront.net/'
S3_NETWORK_TIMEOUT = 10000
S3_NETWORK_RETRY_COUNT = 32
IMAGEKIT_CACHE_TIMEOUT = None
BUCKET_MEDIA = os.environ.get('BUCKET_MEDIA')
BUCKET_MEDIA_CUSTOM_DOMAIN = os.environ.get('BUCKET_MEDIA_CUSTOM_DOMAIN')
BUCKET_MEDIA_DEFAULT_ACL = None
BUCKET_STATIC_CUSTOM_DOMAIN = os.environ.get('BUCKET_STATIC_CUSTOM_DOMAIN')

# ─── GCS ───────────────────────────────────────────────────────────────────
GCS_PROJECT_ID = os.environ.get('GCS_PROJECT_ID')
GCS_BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME', 'litloop_bucket_free')
GCS_CREDENTIALS_JSON = os.environ.get('GCS_CREDENTIALS_JSON')
GCS_PRESIGNED_EXPIRY = int(os.environ.get('GCS_PRESIGNED_EXPIRY') or 3600)
GCS_HMAC_ACCESS_KEY = os.environ.get('GCS_HMAC_ACCESS_KEY')
GCS_HMAC_SECRET = os.environ.get('GCS_HMAC_SECRET')

# ─── CLOUDFLARE R2 ─────────────────────────────────────────────────────────
R2_ACCESS_KEY_ID = os.environ.get('R2_ACCESS_KEY_ID')
R2_SECRET_ACCESS_KEY = os.environ.get('R2_SECRET_ACCESS_KEY')
R2_BUCKET_NAME = os.environ.get('R2_BUCKET_NAME')
R2_ACCOUNT_ID = os.environ.get('R2_ACCOUNT_ID')
R2_ENDPOINT_URL = os.environ.get('R2_ENDPOINT_URL', 'https://{account_id}.r2.cloudflarestorage.com')
R2_PUBLIC_URL = os.environ.get('R2_PUBLIC_URL')

# ─── OAUTH ─────────────────────────────────────────────────────────────────
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_SECRET_KEY")
VK_CLIENT_ID = os.environ.get("VK_CLIENT_ID")
VK_CLIENT_SECRET = os.environ.get("VK_CLIENT_SECRET")
VK_OAUTH_REDIRECT_URI = os.environ.get("VK_OAUTH_REDIRECT_URI", "http://localhost:3001/auth/vk/callback")

# ─── REDIS / CHANNELS / CACHES ─────────────────────────────────────────────
REDIS_LOCATION = "redis://127.0.0.1:6379/1"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [REDIS_LOCATION]},
    },
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_LOCATION,
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    },
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# ─── CELERY ────────────────────────────────────────────────────────────────
CELERY_BROKER_URL = REDIS_LOCATION
CELERY_BROKER_TRANSPORT_OPTIONS = {"visibility_timeout": 86400}
CELERY_RESULT_BACKEND = 'rpc://'
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_SOFT_TIME_LIMIT = 2 * 60 * 60
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERYD_PREFETCH_MULTIPLIER = 1
CELERY_IMPORTS = ['views.tasks', 'posts.tasks']
CELERY_TASK_ALWAYS_EAGER = False

if os.environ.get("TESTING"):
    CELERY_TASK_ALWAYS_EAGER = True

CELERY_BEAT_SCHEDULE = {
    "clear_sessions": {
        "task": "clear_sessions",
        "schedule": crontab(hour=1, minute=1, day_of_week=6),
    },
    "get_list_of_popular_media": {
        "task": "get_list_of_popular_media",
        "schedule": crontab(minute=1, hour="*/10"),
    },
    "update_listings_thumbnails": {
        "task": "update_listings_thumbnails",
        "schedule": crontab(minute=2, hour="*/30"),
    },
    "flush-redis-impressions-likes": {
        "task": "posts.tasks.increment.flush_redis_impressions_likes",
        "schedule": 5.0,
    },
}

CELERY_EMAIL_TASK_CONFIG = {"queue": "short_tasks"}

# ─── EMAIL ─────────────────────────────────────────────────────────────────
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# ─── FFMPEG / ENCODING ─────────────────────────────────────────────────────
FFMPEG_COMMAND = "ffmpeg"
FFPROBE_COMMAND = "ffprobe"
MP4HLS = "mp4hls"
MP4HLS_COMMAND = "/home/mediacms.io/mediacms/Bento4-SDK-1-6-0-637.x86_64-unknown-linux/bin/mp4hls"
MINIMUM_RESOLUTIONS_TO_ENCODE = [240, 360]
CHUNKIZE_VIDEO_DURATION = 60 * 5
VIDEO_CHUNKS_DURATION = 60 * 4

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
