
from litloop_project.settings.base import *
import os

POSTGRES_DB       = os.getenv("DB_NAME")
POSTGRES_PASSWORD = os.getenv("DB_PASSWORD")
POSTGRES_USER     = os.getenv("DB_USER")
POSTGRES_HOST     = os.getenv("DB_HOST")
POSTGRES_PORT     = os.getenv("DB_PORT")

GOOGLE_OAUTH_REDIRECT_URI = "http://localhost:3001/auth/google/callback"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',

        'NAME': 'litloop_db_prod',
        'USER': os.environ.get("POSTGRES_USER"),
        'PASSWORD': os.environ.get("POSTGRES_PASSWORD"),
        'HOST': '127.0.0.1',
        'PORT': '5432'
    }
}
DEBUG = True
ALLOWED_HOSTS=['*']
