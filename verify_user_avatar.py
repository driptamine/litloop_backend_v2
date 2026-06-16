import os
import django
import json
from django.test import RequestFactory
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'litloop_project.settings.dev')
django.setup()

from users.views.user_username import user_username_detail_api

def verify_user_endpoint(username):
    User = get_user_model()
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"User '{username}' not found.")
        return

    factory = RequestFactory()
    
    print(f"--- Testing /users/{username}/ ---")
    request = factory.get(f'/users/{username}/')
    response = user_username_detail_api(request, username)
    data = json.loads(response.content)
    print(f"Status: {response.status_code}")
    print(f"Avatar: {data.get('avatar')}")

if __name__ == "__main__":
    # Test for user 1 (find their username first)
    User = get_user_model()
    u1 = User.objects.get(id=1)
    verify_user_endpoint(u1.username)
