import json
import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.db.models import Max, Value, DateTimeField
from django.db.models.functions import Coalesce
from django.contrib.contenttypes.models import ContentType
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from notifications.models import Notification
from ..models import Chat, Message, VoiceMessage
from ..utils import create_saved_messages_chat
from .common import get_authenticated_user


@require_GET
def chat_list(request):
    """Lists all available chat rooms."""
    chats = list(Chat.objects.all().values('id', 'name', 'image_url', 'description'))
    return JsonResponse({"chats": chats})


@require_GET
def my_chats(request):
    """Lists chats for the current authenticated user, ordered by most recent message."""
    user = get_authenticated_user(request)
    if not user:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    create_saved_messages_chat(user)

    epoch = datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)
    chats = user.chats.annotate(
        last_message_at=Coalesce(
            Max('messages__created_at'),
            Value(epoch),
            output_field=DateTimeField()
        )
    ).order_by('-last_message_at')

    chats_data = []
    for chat in chats:
        is_saved = chat.is_saved_messages
        unread_count = 0 if is_saved else chat.messages.exclude(user=user).filter(is_read=False).count()

        chat_info = {
            "id": chat.id,
            "chat_type": chat.chat_type,
            "name": chat.name,
            "image_url": chat.image_url,
            "description": chat.description,
            "unread_count": unread_count,
            "is_saved_messages": is_saved,
            "other_participant": None,
        }

        if not is_saved:
            other_participant = chat.participants.exclude(id=user.id).first()
            if other_participant:
                chat_info["other_participant"] = {
                    "id": other_participant.id,
                    "username": other_participant.username,
                    "avatar": other_participant.avatar,
                }

        last_message = chat.messages.order_by('-created_at').first()
        if last_message:
            voice = last_message.voice_messages.first()
            voice_data = {
                'id': voice.id,
                'url': voice.url,
                'duration': voice.duration,
                'transcription': voice.transcription,
                'transcription_status': voice.transcription_status,
                'transcription_language': voice.transcription_language,
            } if voice else None

            chat_info["last_message"] = {
                "text": last_message.text,
                "created_at": last_message.created_at,
                "user": last_message.user.username if last_message.user else "AI",
                "is_read": last_message.is_read,
                "attachments": last_message.attachments,
                "voice_message": voice_data
            }

        chats_data.append(chat_info)

    return JsonResponse({"chats": chats_data})


@require_GET
def chat_detail(request, chat_id):
    """Returns messages and target_user for a specific chat room."""
    chat = get_object_or_404(Chat, id=chat_id)
    user = get_authenticated_user(request)

    if user and user.is_authenticated:
        chat.messages.exclude(user=user).filter(is_read=False).update(is_read=True)

    if user and user.is_authenticated:
        other_participant = chat.participants.exclude(id=user.id).first()
    else:
        other_participant = chat.participants.first()

    target_user = {
        "id": other_participant.id,
        "username": other_participant.username,
        "avatar": other_participant.avatar
    } if other_participant else None

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
        "target_user": target_user,
        "messages": messages
    })


@csrf_exempt
@require_POST
def mark_as_read(request, chat_id):
    """Marks all messages in a chat as read for the current user."""
    user = get_authenticated_user(request)
    if not user:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    chat = get_object_or_404(Chat, id=chat_id)

    if not chat.participants.filter(id=user.id).exists():
        return JsonResponse({"error": "Forbidden"}, status=403)

    if chat.is_saved_messages:
        chat.messages.filter(is_read=False).update(is_read=True)
    else:
        chat.messages.exclude(user=user).filter(is_read=False).update(is_read=True)

    return JsonResponse({"status": "success", "chat_id": chat_id})


@csrf_exempt
@require_POST
def send_message(request, chat_id):
    """Sends a new message to a chat room."""
    try:
        user = get_authenticated_user(request)
        if not user:
            return JsonResponse({"error": "Unauthorized"}, status=401)

        if not request.body:
            return JsonResponse({"error": "Request body is empty"}, status=400)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        text = data.get("text", "").strip()
        attachments = data.get("attachments", [])
        voice_message_id = data.get("voice_message_id")

        if not text and not attachments and not voice_message_id:
            return JsonResponse({"error": "Message text, attachment, or voice message is required"}, status=400)

        chat = get_object_or_404(Chat, id=chat_id)

        if not chat.participants.filter(id=user.id).exists():
            chat.participants.add(user)

        message = Message.objects.create(
            chat=chat,
            user=user,
            text=text,
            attachments=attachments
        )

        voice_data = None
        if voice_message_id:
            voice = get_object_or_404(VoiceMessage, id=voice_message_id)
            message.voice_messages.add(voice)
            voice_data = {
                'id': voice.id,
                'url': voice.url,
                'duration': voice.duration,
                'transcription': voice.transcription,
                'transcription_status': voice.transcription_status,
                'transcription_language': voice.transcription_language,
            }

        channel_layer = get_channel_layer()
        message_data = {
            'id': message.id,
            'text': message.text,
            'username': user.username,
            'avatar': user.avatar,
            'created_at': message.created_at.isoformat(),
            'is_read': message.is_read,
            'attachments': message.attachments,
            'voice_message': voice_data
        }

        async_to_sync(channel_layer.group_send)(
            f'chat_{chat.id}',
            {
                'type': 'chat_message',
                'message': message_data
            }
        )

        if chat.is_saved_messages:
            return JsonResponse({
                "status": "sent",
                "chat_id": chat.id,
                "message": message_data
            })

        participants = chat.participants.exclude(id=user.id)
        content_type = ContentType.objects.get_for_model(message)

        for p in participants:
            Notification.objects.create(
                from_user=user,
                to_user=p,
                target_content_type=content_type,
                target_object_id=message.id
            )
            unread_count = chat.messages.exclude(user=p).filter(is_read=False).count()
            if message.text:
                preview = message.text[:50]
            elif voice_data:
                preview = "[Voice Message]"
            elif message.attachments:
                preview = f"[{message.attachments[0].get('type', 'attachment')}]"
            else:
                preview = ""
            async_to_sync(channel_layer.group_send)(
                f'user_{p.id}_notifications',
                {
                    'type': 'send_notification',
                    'notification': {
                        'type': 'new_message',
                        'chat_id': chat.id,
                        'chat_user_id': user.id,
                        'message_id': message.id,
                        'preview': preview,
                        'sender': user.username,
                        'text': preview,
                        'unread_count': unread_count,
                        'created_at': message.created_at.isoformat()
                    }
                }
            )

        return JsonResponse({
            "status": "sent",
            "chat_id": chat.id,
            "message": message_data
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def delete_chat(request, chat_id):
    """Deletes a chat if the user is a participant."""
    if request.method not in ['DELETE', 'POST']:
        return JsonResponse({"error": "Method not allowed"}, status=405)

    user = get_authenticated_user(request)
    if not user:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    chat = get_object_or_404(Chat, id=chat_id)

    if not chat.participants.filter(id=user.id).exists():
        return JsonResponse({"error": "Forbidden"}, status=403)

    if chat.is_saved_messages:
        return JsonResponse({"error": "Cannot delete Saved Messages"}, status=400)

    chat.delete()
    return JsonResponse({"status": "deleted", "id": chat_id})


@require_GET
def saved_messages_chat(request):
    """Return the Saved Messages chat for the current user, creating it if needed."""
    user = get_authenticated_user(request)
    if not user:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    chat = create_saved_messages_chat(user)

    chat.messages.filter(is_read=False).update(is_read=True)

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
            'text': msg.text,
            'created_at': msg.created_at.isoformat(),
            'attachments': msg.attachments,
            'voice_message': voice_data,
        })

    return JsonResponse({
        "id": chat.id,
        "chat_type": chat.chat_type,
        "is_saved_messages": True,
        "messages": messages,
    })
