import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..models import VoiceMessage
from ..gcs import gcs_upload_file
from .common import get_authenticated_user


@csrf_exempt
def upload_chat_attachment(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    user = get_authenticated_user(request)
    if not user:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    file = request.FILES.get('file')
    if not file:
        return JsonResponse({"error": "No file provided"}, status=400)

    ext = file.name.split('.')[-1].lower() if '.' in file.name else ''
    IMG_EXTS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'}
    VID_EXTS = {'mp4', 'webm', 'ogg', 'mov', 'avi', 'mkv'}
    AUD_EXTS = {'mp3', 'wav', 'flac', 'aac', 'm4a', 'opus'}

    if ext in IMG_EXTS:
        file_type = 'photo'
    elif ext in VID_EXTS:
        file_type = 'video'
    elif ext in AUD_EXTS:
        file_type = 'voice'
    else:
        return JsonResponse({"error": "Unsupported file type"}, status=400)

    gcs_path = f"chat_attachments/{uuid.uuid4()}.{ext}"
    file_url = gcs_upload_file(file, gcs_path, content_type=file.content_type)

    return JsonResponse({
        "url": file_url,
        "type": file_type,
        "name": file.name
    })


@csrf_exempt
def voice_message_upload_api(request):
    """
    Upload a voice message — saves via GCS,
    then creates a VoiceMessage record pointing to it.
    """
    user = get_authenticated_user(request)
    if not user:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file provided'}, status=400)

    uploaded_file = request.FILES['file']
    filename = uploaded_file.name
    duration = request.POST.get('duration', 0.0)

    try:
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'webm'
        gcs_path = f"voice_messages/{uuid.uuid4()}.{ext}"

        gcs_upload_file(uploaded_file, gcs_path, content_type=uploaded_file.content_type)

        voice = VoiceMessage.objects.create(
            filename=filename,
            gcs_key=gcs_path,
            user=user,
            duration=float(duration)
        )

        return JsonResponse({
            'success': True,
            'id': voice.id,
            'url': voice.url,
            'duration': voice.duration
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
