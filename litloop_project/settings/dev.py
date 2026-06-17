
from litloop_project.settings.base import *
import os

POSTGRES_DB       = os.getenv("DB_NAME")
POSTGRES_PASSWORD = os.getenv("DB_PASSWORD")
POSTGRES_USER     = os.getenv("DB_USER")
POSTGRES_HOST     = os.getenv("DB_HOST")
POSTGRES_PORT     = os.getenv("DB_PORT")

import dj_database_url

GOOGLE_OAUTH_REDIRECT_URI = "http://localhost:3001/auth/google/callback"

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
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv("DB_NAME", "litloop_db_prod"),
            'USER': os.getenv("DB_USER", os.environ.get("POSTGRES_USER")),
            'PASSWORD': os.getenv("DB_PASSWORD", os.environ.get("POSTGRES_PASSWORD")),
            'HOST': os.getenv("DB_HOST", '127.0.0.1'),
            'PORT': os.getenv("DB_PORT", '5432')
        }
    }
DEBUG = True
ALLOWED_HOSTS=['*']
