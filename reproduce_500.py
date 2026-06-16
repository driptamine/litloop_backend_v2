import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'litloop_project.settings.dev')
django.setup()

from django.test import RequestFactory
from rest_framework.test import force_authenticate
from posts.views import PostCreateView
from users.models import User

# Get a user
user = User.objects.first()
if not user:
    print("No user found for testing")
    exit()

factory = RequestFactory()
view = PostCreateView.as_view()

data = {
    "title": "Test with Media",
    "description": "Test Description",
    "photo_ids": [1],
    "video_ids": [1],
    "track_ids": [1]
}

request = factory.post('/posts/create/', data, content_type='application/json')
force_authenticate(request, user=user)

try:
    response = view(request)
    print(f"Status Code: {response.status_code}")
    print(f"Response Data: {response.data}")
except Exception as e:
    import traceback
    traceback.print_exc()
