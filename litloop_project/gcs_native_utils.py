import os
import json
from google.cloud import storage
from django.conf import settings

def get_gcs_native_client():
    """
    Returns a native GCS storage client.
    Prefers GCS_CREDENTIALS_JSON (path or json string).
    Falls back to default credentials.
    """
    creds_json = getattr(settings, 'GCS_CREDENTIALS_JSON', None)
    
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
            
    return storage.Client(project=getattr(settings, 'GCS_PROJECT_ID', None))
