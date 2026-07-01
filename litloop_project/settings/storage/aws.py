import os


# ─── AWS (Driptamine) ──────────────────────────────────────────────────────
AWS_REGION_DRIPTAMINE = 'eu-north-1'
AWS_ACCESS_KEY_DRIPTAMINE = os.environ.get('AWS_ACCESS_KEY_DRIPTAMINE')
AWS_SECRET_KEY_DRIPTAMINE = os.environ.get('AWS_SECRET_KEY_DRIPTAMINE')
AWS_STORAGE_BUCKET_NAME_DRIPTAMINE = os.environ.get('AWS_STORAGE_BUCKET_DRIPTAMINE', 'litloop_bucket_free')

# ─── AWS (Qalybay) ─────────────────────────────────────────────────────────
AWS_REGION_QALYBAY = 'eu-north-1'
AWS_ACCESS_KEY_QALYBAY = os.environ.get('AWS_ACCESS_KEY_QALYBAY')
AWS_SECRET_KEY_QALYBAY = os.environ.get('AWS_SECRET_KEY_QALYBAY')
AWS_STORAGE_BUCKET_NAME_QALYBAY = os.environ.get('AWS_STORAGE_BUCKET_NAME_QALYBAY')

# ─── S3 GENERIC ────────────────────────────────────────────────────────────
AWS_S3_USE_SSL = os.environ.get('AWS_S3_USE_SSL', 'false').lower() == 'true'
AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL')
AWS_QUERYSTRING_AUTH = False
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_CUSTOM_DOMAIN = os.environ.get('AWS_S3_CUSTOM_DOMAIN')
AWS_CLOUDFRONT_DOMAIN = 'https://xxxxx.cloudfront.net'
CLOUDFRONT_MEDIA_URL = 'https://{media-distribution-id}.cloudfront.net/'
S3_NETWORK_TIMEOUT = 10000
S3_NETWORK_RETRY_COUNT = 32
IMAGEKIT_CACHE_TIMEOUT = None
BUCKET_MEDIA = os.environ.get('BUCKET_MEDIA')
BUCKET_MEDIA_CUSTOM_DOMAIN = os.environ.get('BUCKET_MEDIA_CUSTOM_DOMAIN')
BUCKET_MEDIA_DEFAULT_ACL = None
BUCKET_STATIC_CUSTOM_DOMAIN = os.environ.get('BUCKET_STATIC_CUSTOM_DOMAIN')
