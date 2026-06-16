import boto3
import logging
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view

from photos.models import Photo
from videos.models import Video
from tracks.models import Track

logger = logging.getLogger(__name__)

def get_gcs_s3_client():
    """
    Returns a boto3 client configured for GCS XML API using HMAC keys.
    """
    return boto3.client(
        "s3",
        region_name="auto",
        endpoint_url="https://storage.googleapis.com",
        aws_access_key_id=settings.GCS_HMAC_ACCESS_KEY,
        aws_secret_access_key=settings.GCS_HMAC_SECRET,
    )

@api_view(["POST"])
def gcs_initiate_multipart_upload(request):
    data = request.data
    filename = str(data.get("filename", "unknown"))
    content_type = str(data.get("content_type", "application/octet-stream"))
    media_type = str(data.get("media_type", "media"))

    key = f"{media_type}/{filename}"
    client = get_gcs_s3_client()
    
    try:
        response = client.create_multipart_upload(
            Bucket=settings.GCS_BUCKET_NAME,
            Key=key,
            ContentType=content_type
        )
        return JsonResponse({
            "upload_id": response["UploadId"],
            "key": key,
        })
    except Exception as e:
        logger.exception("GCS HMAC Initiate Failed")
        return JsonResponse({"error": str(e)}, status=500)

@api_view(["POST"])
def gcs_get_part_presigned_url(request):
    data = request.data
    key = data.get("key")
    upload_id = data.get("upload_id")
    part_number = int(data.get("part_number", 1))

    if not key or not upload_id:
        return JsonResponse({"error": "Missing key or upload_id"}, status=400)
    
    client = get_gcs_s3_client()
    try:
        url = client.generate_presigned_url(
            ClientMethod="upload_part",
            Params={
                "Bucket": settings.GCS_BUCKET_NAME,
                "Key": key,
                "UploadId": upload_id,
                "PartNumber": part_number,
            },
            ExpiresIn=3600,
        )
        return JsonResponse({"url": url})
    except Exception as e:
        logger.exception("GCS HMAC Get Part URL Failed")
        return JsonResponse({"error": str(e)}, status=500)

@api_view(["POST"])
def gcs_complete_multipart_upload(request):
    data = request.data
    key = data.get("key")
    upload_id = data.get("upload_id")
    parts = data.get("parts") # Expected: [{"PartNumber": 1, "ETag": "..."}, ...]
    media_type = data.get("media_type")

    client = get_gcs_s3_client()
    try:
        client.complete_multipart_upload(
            Bucket=settings.GCS_BUCKET_NAME,
            Key=key,
            UploadId=upload_id,
            MultipartUpload={"Parts": parts}
        )
        
        # Create DB record
        model = {"photo": Photo, "video": Video, "track": Track}.get(media_type)
        if model:
            filename = key.split("/")[-1]
            obj = model.objects.create(filename=filename, gcs_key=key, status='draft')
            return JsonResponse({
                "status": "completed",
                "id": obj.id,
                "location": f"https://storage.googleapis.com/{settings.GCS_BUCKET_NAME}/{key}"
            })
        return JsonResponse({"status": "completed", "key": key})
    except Exception as e:
        logger.exception("GCS HMAC Complete Failed")
        return JsonResponse({"error": str(e)}, status=500)
