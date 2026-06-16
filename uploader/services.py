from django.conf import settings
from .gcs import gcs_generate_signed_url, gcs_upload_file
from .client import s3_generate_presigned_post

class StorageService:
    @staticmethod
    def get_presigned_url(file_path: str, file_type: str, provider: str = None):
        if provider is None:
            provider = getattr(settings, 'DEFAULT_STORAGE_PROVIDER', 's3')
        
        if provider == 'gcs':
            return {
                "url": gcs_generate_signed_url(file_path=file_path, file_type=file_type),
                "method": "PUT",
                "provider": "gcs"
            }
        else:
            presigned_data = s3_generate_presigned_post(file_path=file_path, file_type=file_type)
            return {
                "url": presigned_data['url'],
                "fields": presigned_data['fields'],
                "method": "POST",
                "provider": "s3"
            }

    @staticmethod
    def upload_file(file_obj, destination_blob_name: str, content_type: str = None, provider: str = None):
        if provider is None:
            provider = getattr(settings, 'DEFAULT_STORAGE_PROVIDER', 's3')
            
        if provider == 'gcs':
            return gcs_upload_file(file_obj, destination_blob_name, content_type)
        else:
            # Implement S3 upload if needed, or use existing boto3 logic
            pass
