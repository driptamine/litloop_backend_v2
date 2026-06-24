import boto3
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def get_r2_client():
    account_id = settings.R2_ACCOUNT_ID or settings.R2_ACCESS_KEY_ID or 'auto'
    endpoint_url = settings.R2_ENDPOINT_URL
    if not endpoint_url:
        endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"

    return boto3.client(
        "s3",
        region_name="auto",
        endpoint_url=endpoint_url,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
    )


def r2_upload_file(file_obj, destination_blob_name: str, content_type: str = None):
    bucket = settings.R2_BUCKET_NAME
    if not bucket:
        raise ValueError("R2_BUCKET_NAME is not configured")

    if not settings.R2_ACCESS_KEY_ID or not settings.R2_SECRET_ACCESS_KEY:
        raise ValueError("R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY must be set")

    client = get_r2_client()
    extra_args = {}
    if content_type:
        extra_args["ContentType"] = content_type

    client.upload_fileobj(file_obj, bucket, destination_blob_name, ExtraArgs=extra_args or None)

    public_url = settings.R2_PUBLIC_URL
    if public_url:
        return f"{public_url.rstrip('/')}/{destination_blob_name}"
    return endpoint_to_url(client.meta.endpoint_url, bucket, destination_blob_name)


def r2_generate_presigned_url(file_path, content_type=None, method="PUT", expiration=3600):
    client = get_r2_client()
    params = {
        "Bucket": settings.R2_BUCKET_NAME,
        "Key": file_path,
    }
    if content_type:
        params["ContentType"] = content_type
    return client.generate_presigned_url(
        ClientMethod=f"{method.lower()}_object",
        Params=params,
        ExpiresIn=expiration,
    )


def endpoint_to_url(endpoint, bucket, key):
    return f"{endpoint}/{bucket}/{key}"
