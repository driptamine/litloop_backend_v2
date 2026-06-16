import boto3
import uuid
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from posts.models import Post, PostPhoto
from photos.models import Photo
from users.auth_utils import jwt_required

# bucket_name = 'litloop-bucket'
s3 = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_QALYBAY,
    aws_secret_access_key=settings.AWS_SECRET_KEY_QALYBAY,
    region_name=settings.AWS_REGION_QALYBAY
)
bucket_name = settings.AWS_STORAGE_BUCKET_NAME_QALYBAY

@csrf_exempt
@jwt_required
def create_post_with_photos(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    # Extract text fields from POST data
    title       = request.POST.get('title', '')
    description = request.POST.get('description', '')

    # Create Post instance first
    post = Post.objects.create(
        title=title,
        description=description,
        author=request.user
    )

    # Handle multiple uploaded files in request.FILES.getlist('photos')
    photos_files = request.FILES.getlist('photos')
    for i, file in enumerate(photos_files):
        # Create Photo instance

        ext = file.name.split('.')[-1]
        s3_key = f"photos/{uuid.uuid4()}.{ext}"

        s3.upload_fileobj(
            Fileobj=file,
            Bucket=bucket_name,
            Key=s3_key,
            ExtraArgs={'ContentType': file.content_type}
        )

        photo = Photo.objects.create(s3_key=s3_key, user=request.user)
        # Link Photo to Post via PostPhoto with order
        PostPhoto.objects.create(post=post, photo=photo, order=i+1)

    return JsonResponse({'success': True, 'post_id': post.id})
