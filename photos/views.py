import json
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from photos.models import PhotoAlbum, PhotoAlbumItem, Photo
from posts.helpers import produce_friendly_token
from users.auth_utils import jwt_required
from litloop_project.gcs_native_utils import get_gcs_native_client


@csrf_exempt
@jwt_required
def photo_album_upload_api(request, photo_album_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    album = get_object_or_404(PhotoAlbum, id=photo_album_id)
    if album.user != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file provided'}, status=400)

    uploaded_file = request.FILES['file']
    filename = uploaded_file.name

    # Save to GCS
    try:
        client = get_gcs_native_client()
        bucket = client.bucket(settings.GCS_BUCKET_NAME)
        key = f"photo/{produce_friendly_token()}_{filename}"
        blob = bucket.blob(key)

        blob.upload_from_file(uploaded_file, content_type=uploaded_file.content_type)

        photo = Photo.objects.create(
            filename=filename,
            gcs_key=key,
            user=request.user,
            status='attached'
        )

        item = album.add_photo(photo)

        return JsonResponse({
            'success': True,
            'photo_id': photo.id,
            'album_id': album.id,
            'item_id': item.id if item else None,
            'location': f"https://storage.googleapis.com/{settings.GCS_BUCKET_NAME}/{key}"
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@jwt_required
def photo_album_add_photo_api(request, photo_album_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    album = get_object_or_404(PhotoAlbum, id=photo_album_id)
    if album.user != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    photo_id = data.get('photo_id')
    if not photo_id:
        return JsonResponse({'error': 'photo_id is required'}, status=400)

    photo = get_object_or_404(Photo, id=photo_id)

    item = album.add_photo(photo)
    if not item:
        return JsonResponse({'error': 'Photo already in album'}, status=400)

    return JsonResponse({
        'success': True,
        'item_id': item.id,
        'photo_id': photo.id,
        'album_id': album.id,
        'ordering': item.ordering
    }, status=201)


@csrf_exempt
@jwt_required
def photo_album_create_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    title = (data.get('title') or '').strip()
    if not title:
        return JsonResponse({'error': 'Title is required'}, status=400)
    if len(title) > 100:
        return JsonResponse({'error': 'Title too long (max 100)'}, status=400)

    description = (data.get('description') or '').strip()

    album = PhotoAlbum(
        title=title,
        description=description,
        user=request.user,
        friendly_token=produce_friendly_token(),
    )
    try:
        album.full_clean(exclude=['friendly_token'])
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    album.save()

    return JsonResponse({
        'id': album.id,
        'title': album.title,
        'description': album.description,
        'friendly_token': album.friendly_token,
        'photo_count': 0,
        'add_date': album.add_date,
    }, status=201)


@csrf_exempt
@jwt_required
def photo_album_detail_api(request, friendly_token):
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET allowed'}, status=405)

    album = get_object_or_404(PhotoAlbum, friendly_token=friendly_token)
    bucket = settings.GCS_BUCKET_NAME

    items = album.photoalbumitem_set.select_related('photo').order_by('ordering', '-action_date')
    photos = []
    for item in items:
        photo = item.photo
        url = None
        if photo.gcs_key:
            url = f"https://storage.googleapis.com/{bucket}/{photo.gcs_key}"
        elif photo.s3_key:
            url = f"https://storage.googleapis.com/{bucket}/{photo.s3_key}"

        photos.append({
            'id': photo.id,
            'pk': photo.pk,
            'gcs_url': url,
            'image': url,
            'url': url,
            'file_path': url,
            'name': photo.title or photo.filename or f'Photo {photo.id}',
            'title': photo.title or photo.filename or f'Photo {photo.id}',
        })

    return JsonResponse({
        'album': {
            'id': album.id,
            'title': album.title,
            'description': album.description,
            'friendly_token': album.friendly_token,
            'photo_count': album.photo.count(),
            'add_date': album.add_date,
        },
        'photos': photos,
    })
