import os


# ─── GCS ───────────────────────────────────────────────────────────────────
GCS_PROJECT_ID = os.environ.get('GCS_PROJECT_ID')
GCS_BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME', 'litloop_bucket_free')
GCS_CREDENTIALS_JSON = os.environ.get('GCS_CREDENTIALS_JSON')
GCS_PRESIGNED_EXPIRY = int(os.environ.get('GCS_PRESIGNED_EXPIRY') or 3600)
GCS_HMAC_ACCESS_KEY = os.environ.get('GCS_HMAC_ACCESS_KEY')
GCS_HMAC_SECRET = os.environ.get('GCS_HMAC_SECRET')
