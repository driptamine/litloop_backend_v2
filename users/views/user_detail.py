from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from users.models import User

def user_detail_api(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'avatar': user.avatar,
        'is_verified': user.is_verified,
        'is_active': user.is_active,
        'is_staff': user.is_staff,
        'created_at': user.created_at.isoformat(),
        'updated_at': user.updated_at.isoformat(),
    }
    
    return JsonResponse(data)
