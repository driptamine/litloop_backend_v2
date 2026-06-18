import os
import datetime
from pathlib import Path
from celery.schedules import crontab
# from environ import Env

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# ENV = Env()
# TEMP_DIRECTORY = "/tmp"
# BASE_DIR = Path(__file__).resolve().parent.parent
SITE_URL = "http://localhost:8000"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'qcss(9#e6wch%rq2zk8i89d3y=h9-#gt@b@g=69zzj#q_pf!(k'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS=['*']

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
    # 'authentication',
    # 'auth',
    'users',
    'posts',
    'videos',
    'photos',
    'likes',
    'comments',
    'artists',
    'tracks',
    'playlists',
    'albums',
    'images',

    # 'media',
    'encoding',
    'litloop_project',
    # 'videos.apps.VideosConfig',
    'actions.apps.ActionsConfig',

    # 'authentication.apps.AuthenticationConfig',
    # 'users.apps.UsersConfig',
    # 'posts.apps.PostsConfig',
    # 'likes.apps.LikesConfig',
    # 'tracks.apps.TracksConfig',
    # 'albums.apps.AlbumsConfig',
    # 'artists.apps.ArtistsConfig',
    # 'images.apps.ImagesConfig',
    # 'uploader.apps.UploaderConfig',
    # 'media.apps.MediaConfig',
]

THIRD_PARTY_APPS = [
    # "allauth",
    # "allauth.account",
    # "allauth.socialaccount",
    'rest_framework',
    'corsheaders',
    'django_extensions',
    'drf_yasg',
    'mptt',
]

INSTALLED_APPS = [
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

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
        }
    }
}



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


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': '127.0.0.1',
        'PORT': '5432'
    }
}


MEDIA_IS_REVIEWED = True
PORTAL_WORKFLOW = "private"

REST_FRAMEWORK = {
    'NON_FIELD_ERRORS_KEY': 'error',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    # 'DEFAULT_PARSER_CLASSES': (
    #     'rest_framework.parsers.JSONParser',
    # )
    # 'DEFAULT_PAGINATION_CLASS':
    #      'tracks.pagination.CustomPagination'
         # 'artcograph_dev.apps.tracks.pagination.CustomPagination'
}

# REST_FRAMEWORK = {
#     'DEFAULT_PAGINATION_CLASS':
#          '<project_name>.pagination.CustomPagination'
# }

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(days=365),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=1),
}

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



MASK_IPS_FOR_ACTIONS = True
# how many seconds a process in running state without reporting progress is
# considered as stale...unfortunately v9 seems to not include time
# some times so raising this high
RUNNING_STATE_STALE = 60 * 60 * 2

# FRIENDLY_TOKEN_LEN = 9

X_FRAME_OPTIONS = "ALLOWALL"


EMAIL_BACKEND = "djcelery_email.backends.CeleryEmailBackend"
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
# CELERY_RESULT_BACKEND = 'redis://localhost:6379'

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_LOCATION,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

REDIS_CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"


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


# OAuth PROVIDERS
# GOOGLE_CLIENT_ID =
# GOOGLE_CLIENT_SECRET =
#
# APPLE_CLIENT_ID =
# APPLE_CLIENT_SECRET =
#
# TWITTER_CLIENT_ID =
# TWITTER_CLIENT_SECRET =
#
# SPOTIFY_CLIENT_ID =
# SPOTIFY_CLIENT_SECRET =
#


from litloop_project.settings.aws import *  # noqa
from litloop_project.settings.celery import *  # noqa
from litloop_project.settings.email import *  # noqa
from litloop_project.settings.ffmpeg import *  # noqa
from litloop_project.settings.session import *  # noqa
