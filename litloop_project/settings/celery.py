from celery.schedules import crontab

from litloop_project.settings.redis import REDIS_LOCATION
from litloop_project.settings.paths import TIME_ZONE


# ─── CELERY ────────────────────────────────────────────────────────────────
CELERY_BROKER_URL = REDIS_LOCATION
CELERY_BROKER_TRANSPORT_OPTIONS = {"visibility_timeout": 86400}
CELERY_RESULT_BACKEND = 'rpc://'
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_SOFT_TIME_LIMIT = 2 * 60 * 60
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERYD_PREFETCH_MULTIPLIER = 1
CELERY_IMPORTS = ['views.tasks', 'posts.tasks']
CELERY_TASK_ALWAYS_EAGER = False

import os
if os.environ.get("TESTING"):
    CELERY_TASK_ALWAYS_EAGER = True

CELERY_BEAT_SCHEDULE = {
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
    "flush-redis-impressions-likes": {
        "task": "posts.tasks.increment.flush_redis_impressions_likes",
        "schedule": 5.0,
    },
}

CELERY_EMAIL_TASK_CONFIG = {"queue": "short_tasks"}

CELERY_TIMEZONE = TIME_ZONE
