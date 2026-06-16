from django.http import JsonResponse
from django.conf import settings
from users.models import User
from users.jwt_auth import decode_jwt

def get_user_from_request(request):
    # Try session auth first
    if request.user.is_authenticated:
        return request.user
    
    # Try JWT auth in header
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1].strip()
        payload = decode_jwt(token)
        if payload:
            user_id = payload.get('user_id')
            try:
                return User.objects.get(id=user_id)
            except User.DoesNotExist:
                return None
    return None

def user_me_view(request):
    user = get_user_from_request(request)
    
    if not user:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'avatar': user.avatar,
        'is_verified': user.is_verified,
        'created_at': user.created_at.isoformat(),
    }
    return JsonResponse(data)
