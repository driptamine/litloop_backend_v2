import os
import django
import json
from django.conf import settings

# Use a more complete settings configuration for testing
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'users',
            'chats',
            'videos',
            'photos',
            'tracks',
            'posts',
            'images',
            'comments',
            'artists',
            'albums',
            'playlists',
            'jobs',
            'links',
            'movies',
            'notes',
            'queries',
            'suggestions',
            'todos',
            'uploader',
            'views',
            'websites',
        ],
        AUTH_USER_MODEL='users.User',
        SECRET_KEY='fake-key',
        TEMP_DIRECTORY='/tmp',
        MEDIA_URL='/media/',
        MEDIA_ROOT='/tmp/media/',
        STATIC_URL='/static/',
        FRIENDLY_TOKEN_LEN=11,
        FRIENDLY_COMMENT_TOKEN_LEN=26,
    )
    django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from users.models import User
from chats.models import Chat, Message
from chats.views import my_chats
from users.token_utils import generate_tokens_for_user

def test_my_chats():
    # Setup database
    from django.core.management import call_command
    call_command('migrate', verbosity=0)

    # 1. Create a user
    user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
    
    # 2. Create another user for DM
    other_user = User.objects.create_user(username='otheruser', email='other@example.com', password='password')
    
    # 3. Create a chat and add our user as participant
    chat = Chat.objects.create(name='test-chat')
    chat.participants.add(user, other_user)
    
    # 4. Add a message
    Message.objects.create(chat=chat, user=user, text="Hello world")
    
    # 5. Generate JWT
    tokens = generate_tokens_for_user(user)
    access_token = tokens['access']
    
    # 6. Mock request
    rf = RequestFactory()
    request = rf.get('/chats/me/', HTTP_AUTHORIZATION=f'Bearer {access_token}')
    request.user = AnonymousUser() # Simulate no session auth, only JWT
    
    # 7. Call the view
    response = my_chats(request)
    print(f"Status: {response.status_code}")
    data = json.loads(response.content.decode())
    print(f"Content: {json.dumps(data, indent=2)}")

    if len(data.get('chats', [])) > 0:
        print("SUCCESS: Found chats for user")
    else:
        print("FAILURE: No chats found for user")

if __name__ == "__main__":
    test_my_chats()
