import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'litloop_project.settings.dev')
django.setup()

from django.test import RequestFactory
from posts.views import post_api_view, update_post_no_drf, delete_post_no_drf
from users.models import User
from posts.models import Post
from photos.models import Photo
from videos.models import Video
from tracks.models import Track

# Get a user
user = User.objects.first()
if not user:
    print("No user found for testing")
    exit()

factory = RequestFactory()

print("--- Testing post_api_view (Consolidated) ---")
# 1. Create a post
create_data = {
    "title": "Non-DRF Initial Title",
    "description": "Non-DRF Initial Description"
}
request = factory.post('/posts/create/', json.dumps(create_data), content_type='application/json')
request.user = user # Mocking jwt_required setting request.user
response = post_api_view(request)
print(f"Create Status Code: {response.status_code}")
if response.status_code != 201:
    print(f"Failed to create post: {response.content}")
    exit()

post_data = json.loads(response.content)
post_id = post_data['id']
print(f"Post created with ID: {post_id}")

# 2. Update the post
photo = Photo.objects.first()
video = Video.objects.first()
track = Track.objects.first()

update_data = {
    "title": "Non-DRF Updated Title",
    "description": "Non-DRF Updated Description",
    "photo_ids": [photo.id] if photo else [],
    "video_ids": [video.id] if video else [],
    "track_ids": [track.id] if track else []
}
request = factory.put(f'/posts/{post_id}/', json.dumps(update_data), content_type='application/json')
request.user = user
response = post_api_view(request, post_id=post_id)
print(f"Update Status Code: {response.status_code}")

updated_data = json.loads(response.content)
if updated_data['title'] == "Non-DRF Updated Title":
    print("Post updated successfully")
else:
    print("Post update failed")

# 3. Delete the post
request = factory.delete(f'/posts/{post_id}/')
request.user = user
response = post_api_view(request, post_id=post_id)
print(f"Delete Status Code: {response.status_code}")

if response.status_code == 204:
    print("Post deleted successfully")
else:
    print(f"Delete failed with status {response.status_code}: {response.content}")


print("\n--- Testing Dedicated Endpoints ---")
# 4. Test dedicated update_no_drf endpoint
post = Post.objects.create(author=user, title="New Post for dedicated test")
post_id = post.id
update_data = {"title": "Dedicated Updated Title"}
request = factory.put(f'/posts/update_no_drf/{post_id}/', json.dumps(update_data), content_type='application/json')
request.user = user
response = update_post_no_drf(request, post_id=post_id)
print(f"Dedicated Update Status Code: {response.status_code}")
if response.status_code == 200:
    print("Dedicated update successful")
else:
    print(f"Dedicated update failed: {response.content}")

# 5. Test dedicated delete_no_drf endpoint
request = factory.delete(f'/posts/delete_no_drf/{post_id}/')
request.user = user
response = delete_post_no_drf(request, post_id=post_id)
print(f"Dedicated Delete Status Code: {response.status_code}")
if response.status_code == 204:
    print("Dedicated delete successful")
else:
    print(f"Dedicated delete failed: {response.content}")
