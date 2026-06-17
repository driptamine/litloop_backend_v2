
from litloop_project.settings.base import *
import os

GOOGLE_OAUTH_REDIRECT_URI = "http://localhost:3001/auth/google/callback"

# DEVELOPMENT SETTINGS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv("DB_NAME", "litloop_db_dev"),
        'USER': os.getenv("DB_USER", "postgres"),
        'PASSWORD': os.getenv("DB_PASSWORD", ""),
        'HOST': os.getenv("DB_HOST", '127.0.0.1'),
        'PORT': os.getenv("DB_PORT", '5432')
    }
}

DEBUG = True
ALLOWED_HOSTS=['*']
