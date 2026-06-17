"""
WSGI config for litloop_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.getenv('DJANGO_SETTINGS_MODULE', 'litloop_project.settings.dev'))

application = get_wsgi_application()
