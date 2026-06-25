import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from ..models import VoiceMessage
from .common import get_authenticated_user
from .launch_spot import launch_spot_transcriber


@csrf_exempt
@require_POST
def trigger_transcription(request, voice_id):
    user = get_authenticated_user(request)
    if not user:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    voice = get_object_or_404(VoiceMessage, id=voice_id)

    if voice.transcription_status == 'completed':
        return JsonResponse({
            "status": "completed",
            "transcription": voice.transcription,
        })

    gcs_path = voice.gcs_key
    if not gcs_path:
        return JsonResponse({"error": "Voice message has no GCS file"}, status=400)

    voice.transcription_status = 'pending'
    voice.save(update_fields=['transcription_status'])

    try:
        launch_spot_transcriber(voice.id, gcs_path)
    except Exception as e:
        voice.transcription_status = 'failed'
        voice.save(update_fields=['transcription_status'])
        return JsonResponse({"error": f"Failed to launch spot VM: {str(e)}"}, status=500)

    return JsonResponse({
        "status": "pending",
        "voice_msg_id": voice.id,
    })


@csrf_exempt
@require_POST
def transcription_callback(request):
    api_key = os.environ.get('TRANSCRIBER_API_KEY', '')
    auth = request.headers.get('Authorization', '')
    expected = f"Bearer {api_key}"
    if auth != expected:
        return JsonResponse({"error": "Forbidden"}, status=403)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    voice_msg_id = data.get('voice_msg_id')
    if not voice_msg_id:
        return JsonResponse({"error": "Missing voice_msg_id"}, status=400)

    voice = get_object_or_404(VoiceMessage, id=voice_msg_id)

    status = data.get('status')
    if status == 'completed':
        voice.transcription = data.get('transcription', '')
        voice.transcription_language = data.get('language', '')
        voice.transcription_status = 'completed'
        voice.transcribed_at = now()
    else:
        voice.transcription_status = 'failed'

    voice.save()

    return JsonResponse({"status": "ok"})


def transcription_status(request, voice_id):
    voice = get_object_or_404(VoiceMessage, id=voice_id)
    return JsonResponse({
        "voice_msg_id": voice.id,
        "status": voice.transcription_status,
        "transcription": voice.transcription,
        "language": voice.transcription_language,
        "transcribed_at": voice.transcribed_at.isoformat() if voice.transcribed_at else None,
    })
