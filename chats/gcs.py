import os
import json
import datetime
import hashlib
import hmac
import base64
from typing import Dict, Any, Optional
from functools import lru_cache
from attrs import define
from google.cloud import storage
from django.conf import settings
import requests

# Note: You might need to add 'google-cloud-storage' and 'attrs' to your requirements.txt

@define
class GCSCredentials:
    project_id: str
    bucket_name: str
    credentials_json: Optional[str] = None  # Path to the service account JSON file or JSON string
    presigned_expiry: int = 3600
    max_size: int = 10 * 1024 * 1024
    hmac_access_key: Optional[str] = None
    hmac_secret: Optional[str] = None

def gcs_get_credentials() -> GCSCredentials:
    project_id = getattr(settings, "GCS_PROJECT_ID", os.environ.get("GCS_PROJECT_ID"))
    bucket_name = getattr(settings, "GCS_BUCKET_NAME", os.environ.get("GCS_BUCKET_NAME"))
    credentials_json = getattr(settings, "GCS_CREDENTIALS_JSON", os.environ.get("GCS_CREDENTIALS_JSON"))
    presigned_expiry = getattr(settings, "GCS_PRESIGNED_EXPIRY", 3600)
    max_size = getattr(settings, "FILE_MAX_SIZE", 10 * 1024 * 1024)
    hmac_access_key = getattr(settings, "GCS_HMAC_ACCESS_KEY", os.environ.get("GCS_HMAC_ACCESS_KEY"))
    hmac_secret = getattr(settings, "GCS_HMAC_SECRET", os.environ.get("GCS_HMAC_SECRET"))

    if not project_id or not bucket_name:
        raise ValueError("GCS credentials (GCS_PROJECT_ID, GCS_BUCKET_NAME) not found.")

    return GCSCredentials(
        project_id=project_id,
        bucket_name=bucket_name,
        credentials_json=credentials_json,
        presigned_expiry=int(presigned_expiry),
        max_size=int(max_size),
        hmac_access_key=hmac_access_key,
        hmac_secret=hmac_secret,
    )

def gcs_get_client():
    credentials = gcs_get_credentials()
    creds_json = credentials.credentials_json
    
    if creds_json:
        try:
            if os.path.exists(creds_json):
                return storage.Client.from_service_account_json(creds_json)
            else:
                info = json.loads(creds_json)
                return storage.Client.from_service_account_info(info)
        except Exception:
            pass
            
    return storage.Client(project=credentials.project_id)

def _hmac_sha256(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

def _get_signed_headers(method, content_type, bucket, object_name, hmac_key, hmac_secret):
    """Build HMAC-signed Authorization header for GCS XML API."""
    date_str = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    string_to_sign = f"{method}\n\n{content_type or ''}\n{date_str}\n/{bucket}/{object_name}"
    signature = base64.b64encode(_hmac_sha256(hmac_secret.encode("utf-8"), string_to_sign)).decode()
    return {
        "Authorization": f"AWS {hmac_key}:{signature}",
        "Date": date_str,
        "Content-Type": content_type or "",
    }

def gcs_generate_signed_url(*, file_path: str, file_type: str, method: str = 'PUT') -> str:
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
    Tries service-account auth first; falls back to HMAC (XML API) if that fails.
    Falls back to Cloudflare R2 if GCS credentials are not configured.
    """
    try:
        credentials = gcs_get_credentials()
    except ValueError:
        return _fallback_r2_upload(file_obj, destination_blob_name, content_type)

    if credentials.hmac_access_key and credentials.hmac_secret:
        return _gcs_upload_hmac(file_obj, destination_blob_name, content_type, credentials)

    client = gcs_get_client()
    bucket = client.bucket(credentials.bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_file(file_obj, content_type=content_type)
    return blob.public_url

def _fallback_r2_upload(file_obj, destination_blob_name, content_type):
    from .r2_utils import r2_upload_file
    return r2_upload_file(file_obj, destination_blob_name, content_type=content_type)

def _gcs_upload_hmac(file_obj, destination_blob_name, content_type, credentials):
    """Upload via GCS XML API using HMAC authentication."""
    url = f"https://storage.googleapis.com/{credentials.bucket_name}/{destination_blob_name}"
    headers = _get_signed_headers(
        "PUT", content_type, credentials.bucket_name,
        destination_blob_name, credentials.hmac_access_key, credentials.hmac_secret
    )
    resp = requests.put(url, data=file_obj, headers=headers)
    resp.raise_for_status()
    return f"https://storage.googleapis.com/{credentials.bucket_name}/{destination_blob_name}"
