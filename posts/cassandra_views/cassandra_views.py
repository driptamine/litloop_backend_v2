from django.http import JsonResponse
from posts.models_cassandra import PostLikeCounter
from uuid import UUID
import redis

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def get_like_count_cached(post_id):
    redis_key = f"post:{post_id}:like_count"

    # Try Redis cache first
    like_count = redis_client.get(redis_key)
    if like_count is not None:
        return int(like_count)

    # Cache miss — query Cassandra

    post_uuid = UUID(str(post_id))
    counter = PostLikeCounter.objects.filter(post_id=post_uuid).first()
    count = counter.like_count if counter else 0

    # Populate Redis cache with expiration (e.g., 5 minutes)
    redis_client.set(redis_key, count, ex=300)

    return count


def post_detail_api(request, post_id):
    from .models import Post
    post = Post.objects.get(id=post_id)
    like_count = get_like_count_cached(post_id)
    return JsonResponse({
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "like_count": like_count,
    })


def like_post(user_id, post_id):
    from uuid import UUID
    post_uuid = UUID(str(post_id))
    user_uuid = UUID(str(user_id))
    from .cassandra_models import PostLike, PostLikeCounter

    existing_like = PostLike.objects.filter(post_id=post_uuid, user_id=user_uuid).first()
    if existing_like:
        return {"status": "already liked"}

    PostLike.create(post_id=post_uuid, user_id=user_uuid)
    PostLikeCounter.objects.filter(post_id=post_uuid).update(like_count=1)

    # Update Redis cache (+1)
    redis_key = f"post:{post_id}:like_count"
    redis_client.incr(redis_key)

    return {"status": "liked"}


def unlike_post(user_id, post_id):
    from uuid import UUID
    post_uuid = UUID(str(post_id))
    user_uuid = UUID(str(user_id))
    from .cassandra_models import PostLike, PostLikeCounter

    existing_like = PostLike.objects.filter(post_id=post_uuid, user_id=user_uuid).first()
    if not existing_like:
        return {"status": "not liked"}

    PostLike.objects.filter(post_id=post_uuid, user_id=user_uuid).delete()
    PostLikeCounter.objects.filter(post_id=post_uuid).update(like_count=-1)

    # Update Redis cache (-1)
    redis_key = f"post:{post_id}:like_count"
    redis_client.decr(redis_key)

    return {"status": "unliked"}
