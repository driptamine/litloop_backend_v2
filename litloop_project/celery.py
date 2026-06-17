from __future__ import absolute_import
from django.conf import settings
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "litloop_project.settings.dev")

broker_url = "amqp://localhost:5672"
BROKER_URL = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')

redis_url = "redis://localhost:6379/0"
rpc_backend = 'rpc://'
# CELERY_IMPORTS = [
#     'views.tasks',
#     'posts.tasks'
# ]

app = Celery("litloop_project", broker=broker_url, backend=rpc_backend)
# app = Celery("litloop_project", broker=broker_url, backend=redis_url, include=['views.tasks'])
# app = Celery("litloop_project")

app.config_from_object("django.conf:settings", namespace='CELERY')
# app.autodiscover_tasks()
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS + settings.INSTALLED_APPS_WITH_APPCONFIGS)

# app.conf.beat_schedule = app.conf.CELERY_BEAT_SCHEDULE
app.conf.broker_transport_options = {"visibility_timeout": 60 * 60 * 24}  # 1 day
# http://docs.celeryproject.org/en/latest/getting-started/brokers/redis.html#redis-caveats


app.conf.worker_prefetch_multiplier = 1
