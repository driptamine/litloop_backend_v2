import os


# ─── CLOUDFLARE R2 ─────────────────────────────────────────────────────────
R2_ACCESS_KEY_ID = os.environ.get('R2_ACCESS_KEY_ID')
R2_SECRET_ACCESS_KEY = os.environ.get('R2_SECRET_ACCESS_KEY')
R2_BUCKET_NAME = os.environ.get('R2_BUCKET_NAME')
R2_ACCOUNT_ID = os.environ.get('R2_ACCOUNT_ID')
R2_ENDPOINT_URL = os.environ.get('R2_ENDPOINT_URL', 'https://{account_id}.r2.cloudflarestorage.com')
R2_PUBLIC_URL = os.environ.get('R2_PUBLIC_URL')
