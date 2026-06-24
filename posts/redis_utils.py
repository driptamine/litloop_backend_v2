import redis

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

IMPRESSION_KEY = 'post:{post_id}:impressions'
LIKES_COUNT_KEY = 'post:{post_id}:likes_count'
LIKED_BY_KEY = 'post:{post_id}:liked_by'
IMPRESSION_FLUSH_KEY = 'post:impressions:pending'
LIKE_FLUSH_KEY = 'post:likes:pending'


# ─── IMPRESSIONS ───

def record_impression(post_id):
    key = IMPRESSION_KEY.format(post_id=post_id)
    pipe = redis_client.pipeline()
    pipe.incr(key)
    pipe.expire(key, 86400)
    pipe.sadd(IMPRESSION_FLUSH_KEY, post_id)
    pipe.execute()


def get_impressions(post_id):
    val = redis_client.get(IMPRESSION_KEY.format(post_id=post_id))
    return int(val) if val else 0


def pop_impression_post_ids():
    ids = redis_client.smembers(IMPRESSION_FLUSH_KEY)
    if ids:
        redis_client.delete(IMPRESSION_FLUSH_KEY)
    return {int(i) for i in ids}


def flush_impressions(post_ids=None):
    from django.db import models
    from posts.models import Post, PostImpression
    ids = post_ids or pop_impression_post_ids()
    if not ids:
        return 0
    pipe = redis_client.pipeline()
    for pid in ids:
        pipe.getdel(IMPRESSION_KEY.format(post_id=pid))
    results = pipe.execute()
    recorded = 0
    for pid, raw in zip(ids, results):
        count = int(raw) if raw else 0
        if count <= 0:
            continue
        try:
            post = Post.objects.get(id=pid)
            PostImpression.objects.bulk_create([
                PostImpression(post=post, user=None) for _ in range(count)
            ])
            Post.objects.filter(id=pid).update(impressions_count=models.F('impressions_count') + count)
            recorded += count
        except Post.DoesNotExist:
            continue
    return recorded


# ─── LIKES ───

def like_post(post_id, user_id):
    liked_by_key = LIKED_BY_KEY.format(post_id=post_id)
    added = redis_client.sadd(liked_by_key, user_id)
    if added:
        pipe = redis_client.pipeline()
        pipe.incr(LIKES_COUNT_KEY.format(post_id=post_id))
        pipe.expire(liked_by_key, 86400)
        pipe.expire(LIKES_COUNT_KEY.format(post_id=post_id), 86400)
        pipe.sadd(LIKE_FLUSH_KEY, post_id)
        pipe.execute()
    return bool(added)


def unlike_post(post_id, user_id):
    liked_by_key = LIKED_BY_KEY.format(post_id=post_id)
    removed = redis_client.srem(liked_by_key, user_id)
    if removed:
        pipe = redis_client.pipeline()
        pipe.decr(LIKES_COUNT_KEY.format(post_id=post_id))
        pipe.sadd(LIKE_FLUSH_KEY, post_id)
        pipe.execute()
    return bool(removed)


def is_liked(post_id, user_id):
    return redis_client.sismember(LIKED_BY_KEY.format(post_id=post_id), user_id)


def get_likes_count(post_id):
    val = redis_client.get(LIKES_COUNT_KEY.format(post_id=post_id))
    if val is not None:
        return int(val)
    return None


def pop_like_post_ids():
    ids = redis_client.smembers(LIKE_FLUSH_KEY)
    if ids:
        redis_client.delete(LIKE_FLUSH_KEY)
    return {int(i) for i in ids}


def flush_likes(post_ids=None):
    from django.db import models
    from posts.models import Post
    ids = post_ids or pop_like_post_ids()
    if not ids:
        return 0
    pipe = redis_client.pipeline()
    liked_by_keys = [LIKED_BY_KEY.format(post_id=pid) for pid in ids]
    for key in liked_by_keys:
        pipe.scard(key)
    like_counts = pipe.execute()
    synced = 0
    for pid, scard in zip(ids, like_counts):
        count = int(scard) if scard else 0
        Post.objects.filter(id=pid).update(likes_count=count)
        synced += 1
    return synced
