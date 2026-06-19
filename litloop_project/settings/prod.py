
from litloop_project.settings.base import *
import os
import dj_database_url

GOOGLE_OAUTH_REDIRECT_URI = "https://litloop.netlify.app/auth/google/callback"

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    # Fallback only if DATABASE_URL is missing
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv("DB_NAME"),
            'USER': os.getenv("DB_USER"),
            'PASSWORD': os.getenv("DB_PASSWORD"),
            'HOST': os.getenv("DB_HOST"),
            'PORT': os.getenv("DB_PORT", "5432"),
            'OPTIONS': {
                'sslmode': 'require',
            }
        }
    }

DEBUG = False
ALLOWED_HOSTS=['*','https://litloop.netlify.app', 'litloop.duckdns.org']
