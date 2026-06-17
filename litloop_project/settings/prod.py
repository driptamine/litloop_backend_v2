
from litloop_project.settings.base import *
import os
import dj_database_url

GOOGLE_OAUTH_REDIRECT_URI = "https://litloop.netlify.app/auth/google/callback"

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True
    )
}

# If DATABASE_URL is not set, fall back to individual variables
if not DATABASES['default']:
    POSTGRES_DB = os.getenv("DB_NAME")
    POSTGRES_PASSWORD = os.getenv("DB_PASSWORD")
    POSTGRES_USER = os.getenv("DB_USER")
    POSTGRES_HOST = os.getenv("DB_HOST")
    POSTGRES_PORT = os.getenv("DB_PORT")

    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': POSTGRES_DB,
        'USER': POSTGRES_USER,
        'PASSWORD': POSTGRES_PASSWORD,
        'HOST': POSTGRES_HOST,
        'PORT': POSTGRES_PORT,
        'OPTIONS': {
            'sslmode': 'require',
        }
    }
DEBUG = False
ALLOWED_HOSTS=['*','https://litloop.netlify.app', 'litloop.duckdns.org']
