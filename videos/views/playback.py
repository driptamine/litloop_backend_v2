import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from uuid import UUID
from datetime import datetime

from videos.models import Video, VideoWatchProgress
try:
    from videos.cassandra_models import UserVideoPlayback
except ImportError:
    UserVideoPlayback = None

import redis

redis_client = redis.StrictRedis(
    host='localhost',  # change if using Docker or external Redis
    port=6379,
    db=0,
    decode_responses=True  # return strings, not bytes
)

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
def save_playback_time(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data          = json.loads(request.body.decode())
        video_id      = data.get('video_id')
        playback_time = data.get('playback_time')

        if not video_id or playback_time is None:
            return JsonResponse({'error': 'Missing fields'}, status=400)

        video = Video.objects.get(id=video_id)

        # Save to Redis
        redis_key = f"playback:{request.user.id}:{video_id}"
        redis_client.set(redis_key, playback_time, ex=86400)

        # Save to Cassandra (optional dependency)
        if UserVideoPlayback is not None:
            UserVideoPlayback.create(
                user_id=UUID(str(request.user.id)),
                video_id=UUID(str(video_id)),
                playback_time=float(playback_time),
                updated_at=datetime.utcnow()
            )

        # Optional: Save to Django model
        obj, _ = VideoWatchProgress.objects.get_or_create(user=request.user, video=video)
        obj.playback_time = float(playback_time)
        obj.save()

        return JsonResponse({'status': 'saved'})

    except Video.DoesNotExist:
        return JsonResponse({'error': 'Video not found'}, status=404)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_playback_time(request):
    video_id = request.GET.get('video_id')
    if not video_id:
        return JsonResponse({'error': 'video_id required'}, status=400)

    redis_key = f"playback:{request.user.id}:{video_id}"
    redis_time = redis_client.get(redis_key)

    if redis_time:
        return JsonResponse({'playback_time': float(redis_time)})

    if UserVideoPlayback is not None:
        try:
            row = UserVideoPlayback.objects(
                user_id=UUID(str(request.user.id)),
                video_id=UUID(str(video_id))
            ).first()

            if row:
                return JsonResponse({'playback_time': float(row.playback_time)})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
