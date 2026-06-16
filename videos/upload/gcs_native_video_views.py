import logging
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from videos.models import Video
from litloop_project.gcs_native_utils import get_gcs_native_client
import datetime

logger = logging.getLogger(__name__)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def gcs_native_initiate_video_upload(request):
    data = request.data
    filename = str(data.get("filename", "unknown"))
    content_type = str(data.get("content_type", "video/mp4"))
    key = f"video/{filename}"
    
    client = get_gcs_native_client()
    bucket = client.bucket(settings.GCS_BUCKET_NAME)
    blob = bucket.blob(key)
    
    try:
        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(minutes=60),
            method="POST",
            content_type=content_type,
            headers={"x-goog-resumable": "start"}
        )
        return JsonResponse({"upload_url": url, "key": key})
    except Exception as e:
        logger.exception("GCS Native Video Initiate Failed")
        return JsonResponse({"error": str(e)}, status=500)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def gcs_native_complete_video_upload(request):
    data = request.data
    key = data.get("key")
    
    client = get_gcs_native_client()
    bucket = client.bucket(settings.GCS_BUCKET_NAME)
    blob = bucket.blob(key)
    
    if not blob.exists():
        return JsonResponse({"error": "File does not exist in GCS"}, status=400)
    
    try:
        filename = key.split("/")[-1]
        obj = Video.objects.create(filename=filename, gcs_key=key, status='draft')
        return JsonResponse({
            "status": "completed",
            "id": obj.id,
            "location": f"https://storage.googleapis.com/{settings.GCS_BUCKET_NAME}/{key}"
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
