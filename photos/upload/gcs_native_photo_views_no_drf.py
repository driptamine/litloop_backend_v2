import logging
import json
import datetime
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from photos.models import Photo
from users.auth_utils import jwt_required
from litloop_project.gcs_native_utils import get_gcs_native_client

logger = logging.getLogger(__name__)

@csrf_exempt
@jwt_required
def gcs_native_initiate_photo_upload(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
    filename = str(data.get("filename", "unknown"))
    content_type = str(data.get("content_type", "image/jpeg"))
    key = f"photo/{filename}"
    
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
        logger.exception("GCS Native Photo Initiate Failed")
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@jwt_required
def gcs_native_complete_photo_upload(request):
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
        obj = Photo.objects.create(filename=filename, gcs_key=key, status='draft', user=request.user)
        
        album_id = data.get("album_id")
        album_item_id = None
        if album_id:
            try:
                from photos.models import PhotoAlbum
                album = PhotoAlbum.objects.get(id=album_id, user=request.user)
                item = album.add_photo(obj)
                if item:
                    album_item_id = item.id
            except (PhotoAlbum.DoesNotExist, ValueError):
                pass # Silently ignore or handle error

        return JsonResponse({
            "status": "completed",
            "id": obj.id,
            "album_item_id": album_item_id,
            "location": f"https://storage.googleapis.com/{settings.GCS_BUCKET_NAME}/{key}"
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
