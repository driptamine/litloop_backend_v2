from storages.backends.gcloud import GoogleCloudStorage
from django.conf import settings

class GCSMediaStorage(GoogleCloudStorage):
    """
    Custom storage for GCS media files.
    """
    def __init__(self, *args, **kwargs):
        kwargs['bucket_name'] = getattr(settings, 'GCS_BUCKET_NAME')
        kwargs['project_id'] = getattr(settings, 'GCS_PROJECT_ID')
        # Credentials can be loaded from GCS_CREDENTIALS_JSON environment variable
        # or by passing them here if needed.
        super().__init__(*args, **kwargs)

class GCSStaticStorage(GoogleCloudStorage):
    """
    Custom storage for GCS static files.
    """
    def __init__(self, *args, **kwargs):
        kwargs['bucket_name'] = getattr(settings, 'GCS_STATIC_BUCKET_NAME', getattr(settings, 'GCS_BUCKET_NAME'))
        kwargs['project_id'] = getattr(settings, 'GCS_PROJECT_ID')
        super().__init__(*args, **kwargs)
