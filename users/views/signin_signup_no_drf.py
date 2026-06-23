import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from users.models import User
from users.token_utils import generate_tokens_for_user
from chats.utils import create_saved_messages_chat

def get_tokens_for_user(user):
    return generate_tokens_for_user(user)

@csrf_exempt
def signup_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    email = data.get('email')
    password = data.get('password')
    avatar = data.get('avatar', '')

    if not email or not password:
        return JsonResponse({'error': 'Email and password are required'}, status=400)

    username = data.get('username')
    if not username:
        # Use email prefix as username
        username = email.split('@')[0].replace('.', '_')
        
    # Handle username collision
    base_username = username
    counter = 1
    while User.objects.filter(username=username).exists():
        import random
        username = f"{base_username}{random.randint(100, 999)}"
        # To avoid infinite loop, though very unlikely with random
        if counter > 10:
            username = f"{base_username}{random.randint(1000, 9999)}"
        counter += 1

    if User.objects.filter(email=email).exists():
        return JsonResponse({'error': 'Email already exists'}, status=400)

    user = User.objects.create_user(username=username, email=email, password=password, avatar=avatar)
    create_saved_messages_chat(user)
    tokens = get_tokens_for_user(user)
    
    return JsonResponse({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'avatar': user.avatar,
        },
        'token': tokens['access'],
        **tokens
    }, status=201)

@csrf_exempt
def signin_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    email_or_username = data.get('email_or_username')
    password = data.get('password')

    if not email_or_username or not password:
        return JsonResponse({'error': 'Email/username and password are required'}, status=400)

    user = authenticate(username=email_or_username, password=password)
    
    if user is None:
        # Try authenticate with email if username failed
        try:
            user_obj = User.objects.get(email=email_or_username)
            user = authenticate(username=user_obj.username, password=password)
        except User.DoesNotExist:
            pass

    if user is not None:
        tokens = get_tokens_for_user(user)
        return JsonResponse({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'avatar': user.avatar,
            },
            'token': tokens['access'],
            **tokens
        }, status=200)
    else:
        return JsonResponse({'error': 'Invalid credentials'}, status=401)
