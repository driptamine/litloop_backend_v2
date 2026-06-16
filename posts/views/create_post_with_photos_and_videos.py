import boto3
import uuid
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from posts.models import Post, PostPhoto
from videos.models import Video
from photos.models import Photo
from posts.utils import multipart_upload
from users.auth_utils import jwt_required

@csrf_exempt
@jwt_required
def create_post_with_photos_and_videos(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    title       = request.POST.get('title', '')
    description = request.POST.get('description', '')

    post = Post.objects.create(
        title=title,
        description=description,
        author=request.user
    )

    # Upload photos
    photos_files = request.FILES.getlist('photos')
    for file in photos_files:
        ext = file.name.split('.')[-1]
        s3_key = f"user_uploads/photos/{uuid.uuid4()}.{ext}"

        multipart_upload(file, s3_key, file.content_type)

        Photo.objects.create(post=post, s3_key=s3_key)

        PostPhoto.objects.create(post=post, photo=photo, order=i+1)

    # Upload videos
    videos_files = request.FILES.getlist('videos')
    for file in videos_files:
        ext = file.name.split('.')[-1]
        s3_key = f"user_uploads/videos/{uuid.uuid4()}.{ext}"

        multipart_upload(file, s3_key, file.content_type)

        Video.objects.create(post=post, s3_key=s3_key)

        PostVideo.objects.create(post=post, video=video, order=i+1)

    return JsonResponse({'message': 'Post created successfully', 'post_id': post.id})
