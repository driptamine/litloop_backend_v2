import os
import uuid
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from users.auth_utils import jwt_required_testable

@csrf_exempt
@jwt_required_testable
def upload_avatar_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    if 'avatar' not in request.FILES:
        return JsonResponse({'error': 'No file provided in "avatar" field.'}, status=400)

    avatar_file = request.FILES['avatar']

    if not avatar_file.content_type.startswith('image/'):
        return JsonResponse({'error': 'File must be an image.'}, status=400)

    ext = os.path.splitext(avatar_file.name)[1]
    if not ext:
        ext = '.jpg' if avatar_file.content_type == 'image/jpeg' else '.png'

    filename = f"avatars/{request.user.id}_{uuid.uuid4()}{ext}"

    try:
        saved_path = default_storage.save(filename, avatar_file)
        public_url = default_storage.url(saved_path)

        user = request.user
        user.avatar = public_url
        user.save(update_fields=['avatar'])

        return JsonResponse({
            'message': 'Avatar uploaded successfully',
            'avatar': public_url
        })
    except Exception as e:
        return JsonResponse({'error': f'Failed to upload avatar: {str(e)}'}, status=500)
