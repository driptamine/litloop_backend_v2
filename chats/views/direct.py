from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from users.models import User
from ..models import Chat
from .common import get_authenticated_user, _chat_list_by_type


@require_GET
def direct_chat_list(request):
    """Lists direct chats for the current user."""
    return _chat_list_by_type(request, 'direct')


@csrf_exempt
def direct_chat_detail(request, user_id):
    """Finds or creates a direct chat between the current user and target user_id."""
    current_user = get_authenticated_user(request)

    if not current_user:
        try:
            current_user = User.objects.get(username='alice')
        except User.DoesNotExist:
            return JsonResponse({"error": "Unauthorized"}, status=401)

    target_user = get_object_or_404(User, id=user_id)

    if current_user == target_user:
        return JsonResponse({"error": "You cannot chat with yourself"}, status=400)

    chat = Chat.objects.filter(participants=current_user).filter(participants=target_user).first()

    if not chat:
        chat = Chat.objects.create(
            chat_type='direct',
            name=f"dm-{min(current_user.id, target_user.id)}-{max(current_user.id, target_user.id)}"
        )
        chat.participants.add(current_user, target_user)

    messages_queryset = chat.messages.all().select_related('user').prefetch_related('voice_messages').order_by('created_at')
    messages = []
    for msg in messages_queryset:
        voice = msg.voice_messages.first()
        voice_data = {
            'id': voice.id,
            'url': voice.url,
            'duration': voice.duration
        } if voice else None

        messages.append({
            'id': msg.id,
            'username': msg.user.username if msg.user else 'AI',
            'avatar': msg.user.avatar if msg.user else None,
            'text': msg.text,
            'created_at': msg.created_at.isoformat(),
            'attachments': msg.attachments,
            'voice_message': voice_data
        })

    return JsonResponse({
        "id": chat.id,
        "chat_type": chat.chat_type,
        "name": chat.name,
        "username": target_user.username,
        "avatar": target_user.avatar,
        "target_user": target_user.username,
        "messages": messages
    })
