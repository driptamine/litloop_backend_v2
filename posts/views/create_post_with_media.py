import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from posts.models import Post, Photo, Video, Track, PostPhoto, PostVideo, PostTrack

@csrf_exempt
def create_post_with_media(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    title = data.get('title')
    body  = data.get('description')
    photo_ids = data.get('photo_ids', [])
    video_ids = data.get('video_ids', [])
    track_ids = data.get('track_ids', [])

    if not body:
        return JsonResponse({'error': 'Missing title or body'}, status=400)

    post = Post.objects.create(title=title, description=body)

    attached_photos, attached_videos, attached_tracks = [], [], []

    for pid in photo_ids:
        try:
            photo = Photo.objects.get(id=pid)
            PostPhoto.objects.create(post=post, photo=photo)
            attached_photos.append(photo.id)
        except Photo.DoesNotExist:
            continue

    for vid in video_ids:
        try:
            video = Video.objects.get(id=vid)
            PostVideo.objects.create(post=post, video=video)
            attached_videos.append(video.id)
        except Video.DoesNotExist:
            continue

    for tid in track_ids:
        try:
            track = Track.objects.get(id=tid)
            PostTrack.objects.create(post=post, track=track)
            attached_tracks.append(track.id)
        except Track.DoesNotExist:
            continue

    return JsonResponse({
        'message': 'Post created successfully',
        'post_id': post.id,
        'photo_ids': attached_photos,
        'video_ids': attached_videos,
        'track_ids': attached_tracks,
    }, status=201)
