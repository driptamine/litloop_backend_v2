import os
import datetime

from pathlib import Path
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

# Sanitize DATABASE_URL globally to avoid "channel binding" and "SNI" errors with Neon/GCP
_db_url = os.environ.get('DATABASE_URL')
if _db_url:
    import re
    # 1. Remove channel_binding parameters
    if 'channel_binding=' in _db_url:
        _db_url = re.sub(r'[?&]channel_binding=[^&]+', '', _db_url)
    
    # 2. Handle Neon SNI / Endpoint ID requirements
    # If it's a neon.tech URL and doesn't have the endpoint option, add it
    if 'neon.tech' in _db_url and 'options=endpoint' not in _db_url:
        # Extract endpoint ID from host (e.g., ep-xxx.us-east-1.aws.neon.tech)
        match = re.search(r'@([^.]+)', _db_url)
        if match:
            endpoint_id = match.group(1)
            separator = '&' if '?' in _db_url else '?'
            _db_url += f"{separator}options=endpoint%3D{endpoint_id}"
    
    os.environ['DATABASE_URL'] = _db_url

AUTHENTICATION_BACKENDS = [
    'users.backends.EmailOrUsernameBackend',  # your custom backend
    'django.contrib.auth.backends.ModelBackend',  # optional fallback
]

# from environ import Env

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# ENV = Env()
# TEMP_DIRECTORY = "/tmp"
# BASE_DIR = Path(__file__).resolve().parent.parent
SITE_URL = "http://localhost:8000"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'qcss(9#e6wch%rq2zk8i89d3y=h9-#gt@b@g=69zzj#q_pf!(k')

# SECURITY WARNING: don't run with debug turned on in production!
# if os.environ.get('ENVIRONMENT') == 'development':
#     DEBUG = False
# else:
#     DEBUG = True

if os.environ.get('ENVIRONMENT') == 'development':
    DEBUG = True
    ALLOWED_HOSTS=['*']
else:
    DEBUG = False
    ALLOWED_HOSTS=['*', 'litloop.netlify.app', 'litloop.duckdns.org']

# ALLOWED_HOSTS=['*']

MINIMUM_RESOLUTIONS_TO_ENCODE = [240, 360]
# FFMPEG_PATH = 'ffmpeg'
# FFMPEG_PATH = ENV.str("FFMPEG_PATH", "ffmpeg")
# FFPROBE_PATH = ENV.str("FFPROBE_PATH", "ffprobe")

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

# AUTH_USER_MODEL = 'authentication.User'
AUTH_USER_MODEL = 'users.User'
# Application definition

LIKES_MODELS = {
    "posts.Post": {
        'serializer': 'posts.serializers.PostSerializer'
    },
    "albums.Album": {
        'serializer': 'albums.serializers.AlbumsSerializer'
    },
    "tracks.Track": {
        'serializer': 'tracks.serializers.TrackSerializer'
    },
}

LOCAL_APPS = [

    'albums',
    'artists',
    'auth_cookie',
    'comments',
    'images',
    'chats',
    'jobs',
    'links',
    'movies',
    'notes',
    'notifications',
    'photos',
    'playlists',
    'posts',
    'queries',
    'suggestions',
    'todos',
    'tracks',
    'users',
    'videos',
    'views',
    'websites',


]

THIRD_PARTY_APPS = [
    # "allauth",
    # "allauth.account",
    # "allauth.socialaccount",
    # 'django_cassandra_engine',
    'channels',
    'corsheaders',
    'django_extensions',
    'mptt',
    'django_celery_beat',
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

    # 'django_cassandra_engine'

    *THIRD_PARTY_APPS,
    *LOCAL_APPS,

]

SITE_ID = 1



MIDDLEWARE = [
    # 'litloop_project.CorsMiddleware',
    # 'litloop_project.middleware.cors.CorsMiddleware',
    'litloop_project.middleware.corss.CorsMiddleware',

    # 'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'litloop_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 'DIRS': [],
        # 'DIRS': [
        #     BASE_DIR + '/templates/',
        # ],
        "DIRS": ["templates"],
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

WSGI_APPLICATION = 'litloop_project.wsgi.application'
ASGI_APPLICATION = 'litloop_project.asgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# CASSANDRA_HOST = os.environ.get('CASSANDRA_HOST', '127.0.0.1')
# CASSANDRA_PORT = os.environ.get('CASSANDRA_PORT', 9042)

# DATABASE_ROUTERS = [
#     'litloop_project.utils.PostgresRouter.PostgresRouter',
#     'litloop_project.utils.CassandraRouter.CassandraRouter',
#
# ]
# Fetch environment variables for PostgreSQL


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#
#         'NAME': 'litloop_db_prod',
#         'USER': os.environ.get("POSTGRES_USER"),
#         'PASSWORD': os.environ.get("POSTGRES_PASSWORD"),
#         'HOST': '127.0.0.1',
#         'PORT': '5432'
#     },


    # 'cassandra_db': {
    #     'ENGINE': 'django_cassandra_engine',
    #     'NAME': 'your_cassandra_keyspace',
    #     'HOST': 'localhost',
    #     'OPTIONS': {
    #         'replication': {
    #             'strategy_class': 'SimpleStrategy',
    #             'replication_factor': 1,
    #         },
    #         'connection': {
    #             'consistency': ConsistencyLevel.LOCAL_QUORUM,
    #             'retry_connect': True,
    #         },
    #         'session': {
    #             'default_timeout': 10,
    #             'default_fetch_size': 10000,
    #         },
    #     }
    # }
# }

AWS_REGION_DRIPTAMINE           = 'eu-north-1'
AWS_ACCESS_KEY_DRIPTAMINE       = os.environ.get('AWS_ACCESS_KEY_DRIPTAMINE')
AWS_SECRET_KEY_DRIPTAMINE       = os.environ.get('AWS_SECRET_KEY_DRIPTAMINE')
AWS_STORAGE_BUCKET_NAME_DRIPTAMINE   = os.environ.get('AWS_STORAGE_BUCKET_DRIPTAMINE', 'litloop_bucket_free')


AWS_REGION_QALYBAY              = 'eu-north-1'
AWS_ACCESS_KEY_QALYBAY          = os.environ.get('AWS_ACCESS_KEY_QALYBAY')
AWS_SECRET_KEY_QALYBAY          = os.environ.get('AWS_SECRET_KEY_QALYBAY')
AWS_STORAGE_BUCKET_NAME_QALYBAY = os.environ.get('AWS_STORAGE_BUCKET_NAME_QALYBAY')

# Google Cloud Storage Settings
GCS_PROJECT_ID = os.environ.get('GCS_PROJECT_ID')
GCS_BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME', 'litloop_bucket_free')
GCS_CREDENTIALS_JSON = os.environ.get('GCS_CREDENTIALS_JSON')
GCS_PRESIGNED_EXPIRY = int(os.environ.get('GCS_PRESIGNED_EXPIRY') or 3600)

GCS_HMAC_ACCESS_KEY = os.environ.get('GCS_HMAC_ACCESS_KEY')
GCS_HMAC_SECRET = os.environ.get('GCS_HMAC_SECRET')

# Cloudflare R2 Settings
R2_ACCESS_KEY_ID = os.environ.get('R2_ACCESS_KEY_ID')
R2_SECRET_ACCESS_KEY = os.environ.get('R2_SECRET_ACCESS_KEY')
R2_BUCKET_NAME = os.environ.get('R2_BUCKET_NAME')
R2_ACCOUNT_ID = os.environ.get('R2_ACCOUNT_ID')
R2_ENDPOINT_URL = os.environ.get('R2_ENDPOINT_URL', 'https://{account_id}.r2.cloudflarestorage.com')
R2_PUBLIC_URL = os.environ.get('R2_PUBLIC_URL')


AWS_S3_USE_SSL = os.environ.get('AWS_S3_USE_SSL', 'false').lower() == 'true'
AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL')
AWS_QUERYSTRING_AUTH = False
IMAGEKIT_CACHE_TIMEOUT = None
# Default bucket settings


# AWS_STORAGE_BUCKET_NAME = 'litloop-bucket'
# AWS_STORAGE_BUCKET_NAME = os.environ.get('BUCKET_STATIC') #comment

AWS_S3_CUSTOM_DOMAIN = os.environ.get('AWS_S3_CUSTOM_DOMAIN')

# BUCKET_MEDIA = os.environ['BUCKET_MEDIA']
BUCKET_MEDIA = os.environ.get('BUCKET_MEDIA') #comment

# CLOUDFRONT
AWS_CLOUDFRONT_DOMAIN = 'https://xxxxx.cloudfront.net'
CLOUDFRONT_MEDIA_URL = 'https://{media-distribution-id}.cloudfront.net/'

S3_NETWORK_TIMEOUT = 10000
S3_NETWORK_RETRY_COUNT = 32
AWS_DEFAULT_ACL = 'public-read'
# Media bucket settings
BUCKET_MEDIA_CUSTOM_DOMAIN = os.environ.get('BUCKET_MEDIA_CUSTOM_DOMAIN')
BUCKET_MEDIA_DEFAULT_ACL = None
BUCKET_STATIC_CUSTOM_DOMAIN = os.environ.get('BUCKET_STATIC_CUSTOM_DOMAIN')

# ...
# DEFAULT_FILE_STORAGE = 'media.custom_storage.CustomS3Boto3Storage'
# STATICFILES_STORAGE = os.environ.get(
#     'STATICFILES_STORAGE', DEFAULT_FILE_STORAGE
# )

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_SECRET_KEY")

VK_CLIENT_ID = os.environ.get("VK_CLIENT_ID")
VK_CLIENT_SECRET = os.environ.get("VK_CLIENT_SECRET")
VK_OAUTH_REDIRECT_URI = os.environ.get("VK_OAUTH_REDIRECT_URI", "http://localhost:3001/auth/vk/callback")

MEDIA_IS_REVIEWED = True
# ...
PORTAL_WORKFLOW = "private"


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

DEFAULT_AUTO_FIELD='django.db.models.AutoField'

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
FRIENDLY_TOKEN_LEN = 11
FRIENDLY_COMMENT_TOKEN_LEN = 26

TEMP_DIRECTORY = "/tmp"  # Don't use a temp directory inside BASE_DIR!!!
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_URL = "/static/"  # where js/css files are stored on the filesystem
# MEDIA_URL = "/media/"  # URL where static files are served from the server
MEDIA_URL = "/uploaded_media/"  # URL where static files are served from the server
STATIC_ROOT = BASE_DIR + "/static/"
# where uploaded + encoded media are stored
# MEDIA_ROOT = BASE_DIR + "/media_files/"
MEDIA_ROOT = BASE_DIR + "/uploaded_media/"
# MEDIA_URL = '/posts_image/'
# MEDIA_ROOT = 'posts_image'

MEDIA_UPLOAD_DIR = "original/"
MEDIA_ENCODING_DIR = "encoded/"
THUMBNAIL_UPLOAD_DIR = f"{MEDIA_UPLOAD_DIR}/thumbnails/"
SUBTITLES_UPLOAD_DIR = f"{MEDIA_UPLOAD_DIR}/subtitles/"
HLS_DIR = os.path.join(MEDIA_ROOT, "hls/")

FFMPEG_COMMAND = "ffmpeg"  # this is the path
FFPROBE_COMMAND = "ffprobe"  # this is the path
MP4HLS = "mp4hls"

MASK_IPS_FOR_ACTIONS = True
# how many seconds a process in running state without reporting progress is
# considered as stale...unfortunately v9 seems to not include time
# some times so raising this high
RUNNING_STATE_STALE = 60 * 60 * 2

# FRIENDLY_TOKEN_LEN = 9

# for videos, after that duration get split into chunks
# and encoded independently
CHUNKIZE_VIDEO_DURATION = 60 * 5
# aparently this has to be smaller than VIDEO_CHUNKIZE_DURATION
VIDEO_CHUNKS_DURATION = 60 * 4

# always get these two, even if upscaling
MINIMUM_RESOLUTIONS_TO_ENCODE = [240, 360]

FILE_STORAGE = "django.core.files.storage.DefaultStorage"

X_FRAME_OPTIONS = "ALLOWALL"
# EMAIL_BACKEND = "djcelery_email.backends.CeleryEmailBackend"
CELERY_EMAIL_TASK_CONFIG = {
    "queue": "short_tasks",
}

POST_UPLOAD_AUTHOR_MESSAGE_UNLISTED_NO_COMMENTARY = ""
# a message to be shown on the author of a media file and only
# only in case where unlisted workflow is used and no commentary
# exists

CANNOT_ADD_MEDIA_MESSAGE = ""

# mp4hls command, part of Bendo4
MP4HLS_COMMAND = "/home/mediacms.io/mediacms/Bento4-SDK-1-6-0-637.x86_64-unknown-linux/bin/mp4hls"


# EMAIL_BACKEND = 'django.core.email.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')


REDIS_LOCATION = "redis://127.0.0.1:6379/1"
# REDIS_LOCATION = "redis://mycache.abc123.use1.cache.amazonaws.com:6379/1"
# CELERY_RESULT_BACKEND = 'redis://localhost:6379'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_LOCATION],
        },
    },
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_LOCATION,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"


# CELERY STUFF
RABBITMQ_LOCATION = "amqp://localhost"

CELERY_IMPORTS = [
    'views.tasks',
    'posts.tasks'
]
INSTALLED_APPS_WITH_APPCONFIGS = [
    'views',
    'posts',
]
# BROKER_URL = REDIS_LOCATION
BROKER_URL = RABBITMQ_LOCATION
CELERY_RESULT_BACKEND = 'rpc://'
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_SOFT_TIME_LIMIT = 2 * 60 * 60
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERYD_PREFETCH_MULTIPLIER = 1

CELERY_BEAT_SCHEDULE = {
    # clear expired sessions, every sunday 1.01am. By default Django has 2week
    # expire date
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
}
# TODO: beat, delete chunks from media root
# chunks_dir after xx days...(also uploads_dir)


LOCAL_INSTALL = False

# this is an option to make the whole portal available to logged in users only
# it is placed here so it can be overrided on local_settings.py
GLOBAL_LOGIN_REQUIRED = False

# TODO: separate settings on production/development more properly, for now
# this should be ok
CELERY_TASK_ALWAYS_EAGER = False
if os.environ.get("TESTING"):
    CELERY_TASK_ALWAYS_EAGER = True

TMDB_API_KEY = os.environ.get('TMDB_API_KEY', 'bceb6c0fefae8ee5a3cf9762ec780d63')




# from config.settings.cors import *  # noqa
# from config.settings.jwt import *  # noqa
# from config.settings.sessions import *  # noqa
# from config.settings.celery import *  # noqa
# from config.settings.sentry import *  # noqa
#
# from config.settings.files_and_storages import *  # noqa
# from config.settings.email_sending import *  # noqa
