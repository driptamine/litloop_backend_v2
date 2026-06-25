import json
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from users.models import User
from ..models import Chat
from .common import get_authenticated_user, _chat_list_by_type


@require_GET
def group_chat_list(request):
    """Lists group chats for the current user."""
    return _chat_list_by_type(request, 'groupchat')


@csrf_exempt
@require_POST
def create_group_chat(request):
    """Creates a new group chat and adds the creator as a participant."""
    try:
        user = get_authenticated_user(request)
        if not user:
            return JsonResponse({"error": "Unauthorized"}, status=401)

        if not request.body:
            return JsonResponse({"error": "Request body is empty"}, status=400)
        data = json.loads(request.body)
        name = data.get("name", "").strip()
        description = data.get("description", "").strip()
        image_url = data.get("image_url", "").strip()
        participant_ids = data.get("participant_ids", [])

        if not name:
            return JsonResponse({"error": "Chat name is required"}, status=400)

        chat = Chat.objects.create(
            chat_type='groupchat',
            name=name[:20],
            description=description,
            image_url=image_url or None,
        )
        chat.participants.add(user)

        if participant_ids:
            participants = User.objects.filter(id__in=participant_ids)
            chat.participants.add(*participants)

        return JsonResponse({
            "status": "created",
            "chat": {
                "id": chat.id,
                "name": chat.name,
                "chat_type": chat.chat_type,
                "description": chat.description,
                "image_url": chat.image_url,
                "participant_count": chat.participants.count(),
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_GET
def group_chat_detail(request, chat_id):
    """Returns group chat info with participants and messages."""
    chat = get_object_or_404(Chat, id=chat_id)
    user = get_authenticated_user(request)

    if user and user.is_authenticated:
        chat.messages.exclude(user=user).filter(is_read=False).update(is_read=True)

    participants = chat.participants.all()
    participants_list = [{
        "id": p.id,
        "username": p.username,
        "avatar": p.avatar,
    } for p in participants]

    messages_queryset = chat.messages.all().select_related('user').prefetch_related('voice_messages').order_by('created_at')
    messages = []
    for msg in messages_queryset:
        voice = msg.voice_messages.first()
        voice_data = {
            'id': voice.id,
            'url': voice.url,
            'duration': voice.duration,
            'transcription': voice.transcription,
            'transcription_status': voice.transcription_status,
            'transcription_language': voice.transcription_language,
        } if voice else None

        messages.append({
            'id': msg.id,
            'username': msg.user.username if msg.user else 'AI',
            'avatar': msg.user.avatar if msg.user else None,
            'text': msg.text,
            'created_at': msg.created_at.isoformat(),
            'is_read': msg.is_read,
            'attachments': msg.attachments,
            'voice_message': voice_data
        })

    return JsonResponse({
        "id": chat.id,
        "chat_type": chat.chat_type,
        "name": chat.name,
        "description": chat.description,
        "image_url": chat.image_url,
        "participants": participants_list,
        "messages": messages,
    })


@csrf_exempt
@require_POST
def group_add_member(request, chat_id):
    """Adds a user to a group chat."""
    user = get_authenticated_user(request)
    if not user:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    chat = get_object_or_404(Chat, id=chat_id)
    if chat.chat_type != 'groupchat':
        return JsonResponse({"error": "Not a group chat"}, status=400)

    if not chat.participants.filter(id=user.id).exists():
        return JsonResponse({"error": "Forbidden"}, status=403)

    try:
        data = json.loads(request.body)
        target_user_id = data.get("user_id")
        if not target_user_id:
            return JsonResponse({"error": "user_id is required"}, status=400)

        target_user = get_object_or_404(User, id=target_user_id)
        chat.participants.add(target_user)

        return JsonResponse({
            "status": "added",
            "user_id": target_user.id,
            "username": target_user.username,
            "participant_count": chat.participants.count(),
        })
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_POST
def group_remove_member(request, chat_id):
    """Removes a user from a group chat."""
    user = get_authenticated_user(request)
    if not user:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    chat = get_object_or_404(Chat, id=chat_id)
    if chat.chat_type != 'groupchat':
        return JsonResponse({"error": "Not a group chat"}, status=400)

    if not chat.participants.filter(id=user.id).exists():
        return JsonResponse({"error": "Forbidden"}, status=403)

    try:
        data = json.loads(request.body)
        target_user_id = data.get("user_id")
        if not target_user_id:
            return JsonResponse({"error": "user_id is required"}, status=400)

        target_user = get_object_or_404(User, id=target_user_id)
        chat.participants.remove(target_user)

        return JsonResponse({
            "status": "removed",
            "user_id": target_user.id,
            "participant_count": chat.participants.count(),
        })
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
