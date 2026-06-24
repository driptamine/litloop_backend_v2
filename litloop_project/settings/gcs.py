import os

GCS_PROJECT_ID = os.environ.get('GCS_PROJECT_ID')
GCS_BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME', 'litloop_bucket_free')
GCS_CREDENTIALS_JSON = os.environ.get('GCS_CREDENTIALS_JSON')
GCS_PRESIGNED_EXPIRY = int(os.environ.get('GCS_PRESIGNED_EXPIRY') or 3600)

GCS_HMAC_ACCESS_KEY = os.environ.get('GCS_HMAC_ACCESS_KEY')
GCS_HMAC_SECRET = os.environ.get('GCS_HMAC_SECRET')

# Cloudflare R2 Settings
R2_ACCESS_KEY_ID = os.environ.get('R2_ACCESS_KEY_ID')
R2_SECRET_ACCESS_KEY = os.environ.get('R2_SECRET_ACCESS_KEY')
R2_BUCKET_NAME = os.environ.get('R2_BUCKET_NAME')
R2_ACCOUNT_ID = os.environ.get('R2_ACCOUNT_ID')
R2_ENDPOINT_URL = os.environ.get('R2_ENDPOINT_URL')
R2_PUBLIC_URL = os.environ.get('R2_PUBLIC_URL')
