import os

from litloop_project.settings.paths import BASE_DIR
from .aws import *
from .gcs import *
from .r2 import *


# ─── STATIC / MEDIA ────────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR + "/static/"
MEDIA_ROOT = BASE_DIR + "/uploaded_media/"
_r2_pub = os.environ.get('R2_PUBLIC_URL', '')
MEDIA_URL = (_r2_pub.rstrip('/') if _r2_pub else '/uploaded_media') + '/'
MEDIA_UPLOAD_DIR = "original/"
MEDIA_ENCODING_DIR = "encoded/"
THUMBNAIL_UPLOAD_DIR = f"{MEDIA_UPLOAD_DIR}/thumbnails/"
SUBTITLES_UPLOAD_DIR = f"{MEDIA_UPLOAD_DIR}/subtitles/"
HLS_DIR = os.path.join(MEDIA_ROOT, "hls/")
DEFAULT_FILE_STORAGE = "litloop_project.r2_storage.R2Storage"
