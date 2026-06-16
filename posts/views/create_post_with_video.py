# https://chatgpt.com/c/6832c06f-3110-800c-bd4d-a84a93eb9fc6
from django.http import JsonResponse
from videos.models import Video
from posts.models import Post, PostVideo


def create_post_with_video(request):

    video_ids = request.POST.get('video_ids')
    title     = request.POST.get('title')

    if not video_ids:
        return JsonResponse({"error": "Missing video_ids"}, status=400)

    try:
        video = Video.objects.get(id=video_id, status='draft')
    except Video.DoesNotExist:
        return JsonResponse({"error": "Invalid or already used video"}, status=404)

    videos = Video.objects.filter(id__in=video_ids, status='draft')

    post = Post.objects.create(title=title)

    for video in videos:
        PostVideo.objects.create(post=post, video=video)
        video.status = 'attached'
        video.save(update_fields=['status'])

    return JsonResponse({
        "post_id": post.id,
        "title": post.title,
        "video_id": [video.id for video in videos],
        "video_url": [video.url for video in videos]
    }, status=201)
