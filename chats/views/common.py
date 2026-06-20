import datetime
import json
from django.http import JsonResponse
from django.db.models import Max, Value, DateTimeField
from django.db.models.functions import Coalesce
from ..utils import get_user_from_jwt
from ..models import Chat


def get_authenticated_user(request):
    """Helper to get user from JWT or session."""
    user = get_user_from_jwt(request)
    if user and user.is_authenticated:
        return user
    if request.user.is_authenticated:
        return request.user
    return None


def _chat_list_by_type(request, chat_type):
    """Shared helper for listing chats filtered by type."""
    user = get_authenticated_user(request)
    if not user:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    epoch = datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)
    chats = user.chats.filter(chat_type=chat_type).annotate(
        last_message_at=Coalesce(
            Max('messages__created_at'),
            Value(epoch),
            output_field=DateTimeField()
        )
    ).order_by('-last_message_at')

    chats_data = []
    for chat in chats:
        other_participant = chat.participants.exclude(id=user.id).first()
        unread_count = chat.messages.exclude(user=user).filter(is_read=False).count()

        chat_info = {
            "id": chat.id,
            "chat_type": chat.chat_type,
            "name": chat.name,
            "image_url": chat.image_url,
            "description": chat.description,
            "unread_count": unread_count,
            "other_participant": {
                "id": other_participant.id,
                "username": other_participant.username,
                "avatar": other_participant.avatar
            } if other_participant else None
        }

        last_message = chat.messages.order_by('-created_at').first()
        if last_message:
            voice = last_message.voice_messages.first()
            voice_data = {
                'id': voice.id,
                'url': voice.url,
                'duration': voice.duration
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
