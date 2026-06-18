import os
import json
import datetime
from typing import Dict, Any, Optional
from functools import lru_cache
from attrs import define
from google.cloud import storage
from django.conf import settings

# Note: You might need to add 'google-cloud-storage' and 'attrs' to your requirements.txt

@define
class GCSCredentials:
    project_id: str
    bucket_name: str
    credentials_json: Optional[str] = None  # Path to the service account JSON file or JSON string
    presigned_expiry: int = 3600
    max_size: int = 10 * 1024 * 1024

def gcs_get_credentials() -> GCSCredentials:
    # We follow the pattern from uploader/client.py but for GCS
    # These should be added to your .env and settings
    project_id = getattr(settings, "GCS_PROJECT_ID", os.environ.get("GCS_PROJECT_ID"))
    bucket_name = getattr(settings, "GCS_BUCKET_NAME", os.environ.get("GCS_BUCKET_NAME"))
    print(f"DEBUG: Using GCS bucket: {bucket_name}")
    credentials_json = getattr(settings, "GCS_CREDENTIALS_JSON", os.environ.get("GCS_CREDENTIALS_JSON"))
    presigned_expiry = getattr(settings, "GCS_PRESIGNED_EXPIRY", 3600)
    max_size = getattr(settings, "FILE_MAX_SIZE", 10 * 1024 * 1024)

    if not project_id or not bucket_name:
        raise ValueError("GCS credentials (GCS_PROJECT_ID, GCS_BUCKET_NAME) not found.")

    return GCSCredentials(
        project_id=project_id,
        bucket_name=bucket_name,
        credentials_json=credentials_json,
        presigned_expiry=int(presigned_expiry),
        max_size=int(max_size)
    )

def gcs_get_client():
    credentials = gcs_get_credentials()
    creds_json = credentials.credentials_json
    
    if creds_json:
        try:
            # Check if it's a file path
            if os.path.exists(creds_json):
                return storage.Client.from_service_account_json(creds_json)
            else:
                # Assume it's a JSON string
                info = json.loads(creds_json)
                return storage.Client.from_service_account_info(info)
        except Exception:
            # If parsing fails, fall back to default
            pass
            
    # Fallback to default credentials (e.g. if running on GCE/GAE/GKE or GOOGLE_APPLICATION_CREDENTIALS is set)
    return storage.Client(project=credentials.project_id)

def gcs_generate_signed_url(*, file_path: str, file_type: str, method: str = 'PUT') -> str:
    """
    Generates a signed URL for GCS.
    Note: For 'POST' (browser uploads), GCS uses a different mechanism (Signed Policy),
    but 'PUT' is commonly used for direct uploads.
    """
    credentials = gcs_get_credentials()
    client = gcs_get_client()
    bucket = client.bucket(credentials.bucket_name)
    blob = bucket.blob(file_path)

    url = blob.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(seconds=credentials.presigned_expiry),
        method=method,
        content_type=file_type,
    )

    return url

def gcs_upload_file(file_obj, destination_blob_name: str, content_type: str = None):
    """
    Uploads a file object to GCS.
    """
    credentials = gcs_get_credentials()
    client = gcs_get_client()
    bucket = client.bucket(credentials.bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_file(file_obj, content_type=content_type)
    return blob.public_url
