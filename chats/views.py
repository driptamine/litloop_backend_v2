import os
import json
import datetime
import uuid
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.files.storage import default_storage
from users.models import User
from django.db.models import F, Max, Value, DateTimeField
from django.db.models.functions import Coalesce
from .models import Chat, Message, VoiceMessage
from .gcs import gcs_upload_file
from .utils import get_user_from_jwt, get_ice_servers

@csrf_exempt
def get_ice_servers_api(request):
    """
    API endpoint to retrieve ICE servers for WebRTC.
    """
    return JsonResponse({
        "ice_servers": get_ice_servers()
    })
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from notifications.models import Notification
from django.contrib.contenttypes.models import ContentType

try:
    from google import genai
    client = genai.Client(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))
except ImportError:
    client = None

def get_authenticated_user(request):
    """Helper to get user from JWT or session."""
    user = get_user_from_jwt(request)
    if user and user.is_authenticated:
        return user
    if request.user.is_authenticated:
        return request.user
    return None

# ─── Direct Chat Views ─────────────────────────────────────────────

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

# ─── Group Chat Views ─────────────────────────────────────────────

@require_GET
def group_chat_list(request):
    """Lists group chats for the current user."""
    return _chat_list_by_type(request, 'groupchat')

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
            'duration': voice.duration
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

    # Annotate with the timestamp of the last message and order by it
    # Use Coalesce to handle chats with no messages (they'll have a very old date)
    # We use output_field=DateTimeField() to ensure compatibility across DB backends
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
        # For direct chats, find the other participant
        other_participant = chat.participants.exclude(id=user.id).first()

        # Calculate unread count for this user
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

        # Get the last message
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

@require_GET
def chat_detail(request, chat_id):
    """Returns messages and target_user for a specific chat room."""
    chat = get_object_or_404(Chat, id=chat_id)
    user = get_authenticated_user(request)

    # Mark messages as read if the user is a participant
    if user and user.is_authenticated:
        chat.messages.exclude(user=user).filter(is_read=False).update(is_read=True)

    # Identify the other participant
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
            'duration': voice.duration
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

    # Check if user is a participant
    if not chat.participants.filter(id=user.id).exists():
        return JsonResponse({"error": "Forbidden"}, status=403)

    # Mark messages as read (exclude messages sent by the user themselves)
    chat.messages.exclude(user=user).filter(is_read=False).update(is_read=True)

    return JsonResponse({"status": "success", "chat_id": chat_id})

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

        # Upload to GCS
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

        # Ensure user is a participant
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
                'duration': voice.duration
            }

        # Broadcast to WebSocket
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

        # 1. Send to Chat Group
        async_to_sync(channel_layer.group_send)(
            f'chat_{chat.id}',
            {
                'type': 'chat_message',
                'message': message_data
            }
        )

        # 2. Send Notifications to other participants
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

    # Check if user is a participant
    if not chat.participants.filter(id=user.id).exists():
        return JsonResponse({"error": "Forbidden"}, status=403)

    chat.delete()
    return JsonResponse({"status": "deleted", "id": chat_id})

@csrf_exempt
@require_GET
def chat_with_gemini(request):
    """AI Chat view that persists messages to the database."""
    user_query = request.GET.get("q", "").strip()

    if not user_query:
        return HttpResponseBadRequest("Missing 'q' query parameter.")

    if not client:
        return JsonResponse({"error": "Gemini client not configured"}, status=500)

    try:
        # 1. Get or Create a special Gemini Chat room
        gemini_chat, _ = Chat.objects.get_or_create(
            name="gemini-ai",
            defaults={"description": "AI Assistant Conversation"}
        )

        # 2. Save User Message
        user = get_authenticated_user(request)
        Message.objects.create(
            chat=gemini_chat,
            user=user,
            text=user_query
        )

        # 3. Get AI Response
        response = client.models.generate_content(
            contents=user_query,
            model='gemini-2.0-flash-001'
        )
        ai_text = response.text

        # 4. Save AI Message (no user assigned)
        Message.objects.create(
            chat=gemini_chat,
            text=ai_text
        )

        return JsonResponse({
            "response": ai_text
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
