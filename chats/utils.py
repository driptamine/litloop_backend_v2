from django.contrib.auth.models import AnonymousUser
from users.models import User
from users.jwt_auth import decode_jwt
from .models import Chat

def get_user_from_jwt(request):
    """
    Manually extracts and verifies a JWT token from the request header
    using the project's custom decode_jwt logic.
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        # Fallback to META for older Django/test clients
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
    if not auth_header or not auth_header.startswith('Bearer '):
        return AnonymousUser()

    try:
        token = auth_header.split(' ')[1].strip()
        payload = decode_jwt(token)
        
        if not payload:
            return AnonymousUser()
            
        user_id = payload.get('user_id')
        if not user_id:
            return AnonymousUser()
            
        try:
            user = User.objects.get(id=user_id)
            return user
        except User.DoesNotExist:
            return AnonymousUser()
            
    except Exception:
        return AnonymousUser()

def create_saved_messages_chat(user):
    """Create or return existing Saved Messages chat for a user."""
    chat = Chat.objects.filter(is_saved_messages=True, participants=user).first()
    if chat:
        return chat
    chat = Chat.objects.create(
        chat_type='direct',
        is_saved_messages=True,
        name=f'saved-{user.id}',
    )
    chat.participants.add(user)
    return chat

def get_ice_servers():
    """
    Returns a list of ICE servers (STUN/TURN) for WebRTC.
    In a production app, you might want to fetch these from a service like Twilio or Xirsys.
    """
    return [
        {"urls": "stun:stun.l.google.com:19302"},
        {"urls": "stun:stun1.l.google.com:19302"},
        {"urls": "stun:stun2.l.google.com:19302"},
    ]
