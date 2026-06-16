import redis
from posts.models_cassandra import PostLikeCounter
from uuid import UUID
from django.http import JsonResponse
from .models import Post
from .utils import get_like_counts_cached  # new batch function

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def get_like_counts_cached(post_ids):
    """
    Given a list of post_id strings, return a dict { post_id: like_count }.
    Uses Redis mget for batch fetch, falls back to Cassandra for cache misses.
    """
    # Prepare Redis keys
    keys = [f"post:{pid}:like_count" for pid in post_ids]

    # Batch GET
    values = redis_client.mget(keys)

    result = {}
    misses = []
    for pid, val in zip(post_ids, values):
        if val is not None:
            result[pid] = int(val)
        else:
            misses.append(pid)

    if misses:
        # Fallback: query Cassandra for all misses
        # (this is still N but N << total; you can optimize further with async calls)
        for pid in misses:
            uuid = UUID(pid)
            counter = PostLikeCounter.objects.filter(post_id=uuid).first()
            count = counter.like_count if counter else 0
            result[pid] = count
            # Warm the cache with a TTL
            redis_client.set(f"post:{pid}:like_count", count, ex=300)

    return result



def user_feed_api(request):
    # 1. Pull your posts in one SQL query
    posts = list(Post.objects.all().order_by('-created_at')[:20])

    # 2. Extract IDs and batch-fetch like counts from Redis/Cassandra
    post_ids = [str(post.id) for post in posts]
    like_counts = get_like_counts_cached(post_ids)

    # 3. Build response
    feed = []
    for post in posts:
        feed.append({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "like_count": like_counts.get(str(post.id), 0),
        })

    return JsonResponse({"feed": feed})
