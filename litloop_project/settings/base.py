import os
from pathlib import Path
from dotenv import load_dotenv

# Load .credentials/*.env for local dev
credentials_dir = Path(__file__).resolve().parent.parent.parent / '.credentials'
if credentials_dir.exists():
    for env_file in ['database.env', 'neon.env', 'aws.env', 'google_cloud_storage.env', 'r2.env', 'oauth.env', 'brave.env', 'twitch.env', 'redis.env', 'misc.env']:
        load_dotenv(credentials_dir / env_file)
# Also load .env from project root (deployment writes a single .env)
load_dotenv(Path(__file__).resolve().parent.parent.parent / '.env')

# ─── SUB-MODULE SETTINGS ───────────────────────────────────────────────────
from litloop_project.settings.paths import *
from litloop_project.settings.database import *
from litloop_project.settings.storage import *
from litloop_project.settings.redis import *
from litloop_project.settings.celery import *
from litloop_project.settings.oauth import *
from litloop_project.settings.email import *
from litloop_project.settings.ffmpeg import *
from litloop_project.settings.misc import *

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
    'channels', 'corsheaders', 'django_extensions', 'mptt', 'django_celery_beat', 'storages',
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
