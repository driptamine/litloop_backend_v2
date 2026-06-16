import json
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from users.token_utils import generate_tokens_for_user
from users.services import user_get_or_create
from users.avatar_utils import download_and_save_avatar
from .services import google_get_access_token, google_get_user_info

@csrf_exempt
def google_login_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    code = data.get('code')
    if not code:
        return JsonResponse({'error': 'Code is required'}, status=400)

    # Determine redirect_uri based on origin or settings
    origin = request.META.get('HTTP_ORIGIN', '')
    if origin == 'https://litloop.netlify.app':
        redirect_uri = "https://litloop.netlify.app/auth/google/callback"
    elif origin == 'http://localhost:3000':
        redirect_uri = "http://localhost:3000/auth/google/callback"
    elif origin == 'http://localhost:3001':
        redirect_uri = "http://localhost:3001/auth/google/callback"
    else:
        redirect_uri = getattr(settings, 'GOOGLE_OAUTH_REDIRECT_URI', "http://localhost:3001/auth/google/callback")

    try:
        token_data = google_get_access_token(code=code, redirect_uri=redirect_uri)
        access_token = token_data.get('access_token')
        
        if not access_token:
            return JsonResponse({'error': 'Failed to obtain access token'}, status=400)

        user_data = google_get_user_info(access_token=access_token)
        
        google_picture = user_data.get('picture', '')
        profile_data = {
            'email': user_data['email'],
            'avatar': google_picture,
            'username': user_data['email'].split('@')[0].replace('.', '_')
        }

        user, created = user_get_or_create(**profile_data)

        # Download and re-host the Google avatar to avoid hotlink 429s
        local_avatar = download_and_save_avatar(google_picture, user.id)
        if local_avatar != google_picture:
            user.avatar = local_avatar
            user.save(update_fields=["avatar"])
        
        # Generate tokens
        tokens = generate_tokens_for_user(user)
        
        return JsonResponse({
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'avatar': user.avatar,
            },
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'created': created
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def vk_login_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    code = data.get('code')
    if not code:
        return JsonResponse({'error': 'Code is required'}, status=400)

    # Determine redirect_uri based on origin or settings
    origin = request.META.get('HTTP_ORIGIN', '')
    if origin == 'https://litloop.netlify.app':
        redirect_uri = "https://litloop.netlify.app/auth/vk/callback"
    elif origin == 'http://localhost:3000':
        redirect_uri = "http://localhost:3000/auth/vk/callback"
    elif origin == 'http://localhost:3001':
        redirect_uri = "http://localhost:3001/auth/vk/callback"
    else:
        redirect_uri = getattr(settings, 'VK_OAUTH_REDIRECT_URI', "http://localhost:3001/auth/vk/callback")

    try:
        token_data = vk_get_access_token(code=code, redirect_uri=redirect_uri)
        access_token = token_data.get('access_token')
        user_id = token_data.get('user_id')
        email = token_data.get('email') # VK returns email in token response if requested
        
        if not access_token or not user_id:
            return JsonResponse({'error': 'Failed to obtain access token or user ID from VK'}, status=400)

        vk_user_data = vk_get_user_info(access_token=access_token, user_id=user_id)
        
        # If email was not in token response, use user_id
        if not email:
            email = f"vk_{user_id}@litloop.com"
            
        vk_picture = vk_user_data.get('photo_max', '')
        first_name = vk_user_data.get('first_name', '')
        last_name = vk_user_data.get('last_name', '')
        
        username = f"{first_name}_{last_name}".lower() or f"vk_{user_id}"
        
        profile_data = {
            'email': email,
            'avatar': vk_picture,
            'username': username
        }

        user, created = user_get_or_create(**profile_data)

        # Download and re-host the VK avatar
        if vk_picture:
            local_avatar = download_and_save_avatar(vk_picture, user.id)
            if local_avatar != vk_picture:
                user.avatar = local_avatar
                user.save(update_fields=["avatar"])
        
        # Generate tokens
        tokens = generate_tokens_for_user(user)
        
        return JsonResponse({
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'avatar': user.avatar,
            },
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'created': created
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
