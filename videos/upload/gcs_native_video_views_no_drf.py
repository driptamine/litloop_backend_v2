import logging
import json
import datetime
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from videos.models import Video
from users.auth_utils import jwt_required
from litloop_project.gcs_native_utils import get_gcs_native_client

logger = logging.getLogger(__name__)

@csrf_exempt
@jwt_required
def gcs_native_initiate_video_upload(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
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

@csrf_exempt
@jwt_required
def gcs_native_complete_video_upload(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
    key = data.get("key")
    if not key:
        return JsonResponse({"error": "Missing key"}, status=400)
    
    client = get_gcs_native_client()
    bucket = client.bucket(settings.GCS_BUCKET_NAME)
    blob = bucket.blob(key)
    
    if not blob.exists():
        return JsonResponse({"error": "File does not exist in GCS"}, status=400)
    
    try:
        filename = key.split("/")[-1]
        obj = Video.objects.create(filename=filename, gcs_key=key, status='draft', user=request.user)
        return JsonResponse({
            "status": "completed",
            "id": obj.id,
            "location": f"https://storage.googleapis.com/{settings.GCS_BUCKET_NAME}/{key}"
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
