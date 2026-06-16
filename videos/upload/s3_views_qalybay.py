import boto3
import json
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from videos.models import Video
from photos.models import Photo
from tracks.models import Track
# from tracks.models import TrackV2
import logging

logger = logging.getLogger(__name__)


s3 = boto3.client(
    "s3",
    region_name=settings.AWS_REGION_QALYBAY,
    aws_access_key_id=settings.AWS_ACCESS_KEY_QALYBAY,
    aws_secret_access_key=settings.AWS_SECRET_KEY_QALYBAY,

)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_presigned_url(request):
    """
    Step 1: Initiate multipart upload.
    """
    data = request.data

    filename     = str(data["filename"])
    content_type = str(data["content_type"])

    media_type   = str(data["media_type"])

    if media_type == "photo":
        key='photo'
    elif media_type == 'video':
        key='video'
    else:
        key='track'

    response = s3.create_multipart_upload(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME_QALYBAY,
        # Key=filename,
        Key=f"{key}/{filename}",
        ContentType=content_type,
    )

    return JsonResponse({
        "upload_id": response["UploadId"],
        "key": response["Key"],
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_presigned_url(request):
    """
    Step 2: Generate a presigned URL for a specific part number.
    """
    data = request.data

    upload_id   = data["upload_id"]
    key         = data["key"]
    part_number = int(data["part_number"])

    url = s3.generate_presigned_url(
        ClientMethod="upload_part",
        Params={
            "Bucket": settings.AWS_STORAGE_BUCKET_NAME_QALYBAY,
            "Key": key,
            "UploadId": upload_id,
            "PartNumber": part_number,
        },
        ExpiresIn=3600,
    )

    return JsonResponse({"url": url})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def complete_upload(request):
    """
    Step 3: Finalize multipart upload.
    """
    data = request.data

    upload_id  = data["upload_id"]
    key        = data["key"]
    parts      = data["parts"]  # [{ PartNumber: 1, ETag: "..." }, ...]
    media_type = data["media_type"]

    response = s3.complete_multipart_upload(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME_QALYBAY,
        Key=key,
        UploadId=upload_id,
        MultipartUpload={"Parts": parts},
    )
    key = response['Key']
    cloudfront_url = f"https://dgsmmq1mgfewt.cloudfront.net/{key}"

    # Object.objects.create()
    # https://chatgpt.com/c/68081760-2fc4-800c-8946-98760a9575f5
    #

    print("media_type:", media_type)
    # print("available models:", {
    #     "photo": Photo,
    #     "video": Video,
    #     "track": Track
    # })
    model = {
        "photo": Photo,
        "video": Video,
        "track": Track
    }.get(media_type)

    if not model:
        return JsonResponse({"error": f"Unknown media type: {media_type}"}, status=400)

    if not isinstance(key, str):
        return JsonResponse({"error": "Invalid key"}, status=500)

    filename = key.split("/")[-1]

    try:
        obj = model.objects.create(filename=filename, s3_key=key, status='draft', user=request.user)
        
        album_id = data.get("album_id")
        album_item_id = None
        if album_id and media_type == 'photo':
            try:
                from photos.models import PhotoAlbum
                album = PhotoAlbum.objects.get(id=album_id, user=request.user)
                item = album.add_photo(obj)
                if item:
                    album_item_id = item.id
            except (PhotoAlbum.DoesNotExist, ValueError):
                pass
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": f"Model creation failed: {str(e)}"}, status=500)

    # ensure cloudfront_url is defined
    try:
        return JsonResponse({
            "status": "completed",
            "id": obj.id,
            "album_item_id": album_item_id,
            "location": cloudfront_url  # make sure this is defined above
        })
    except NameError as e:
        return JsonResponse({"error": f"Missing cloudfront_url: {str(e)}"}, status=500)


def create_video(request):
    title = request.POST.get('title', '')
    data = request.data
