import redis

_redis_client = None

def get_redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
    return _redis_client

IMPRESSION_KEY = 'post:{post_id}:impressions'
LIKES_COUNT_KEY = 'post:{post_id}:likes_count'
LIKED_BY_KEY = 'post:{post_id}:liked_by'
IMPRESSION_FLUSH_KEY = 'post:impressions:pending'
LIKE_FLUSH_KEY = 'post:likes:pending'


# ─── IMPRESSIONS ───

def record_impression(post_id):
    r = get_redis()
    key = IMPRESSION_KEY.format(post_id=post_id)
    pipe = r.pipeline()
    pipe.incr(key)
    pipe.expire(key, 86400)
    pipe.sadd(IMPRESSION_FLUSH_KEY, post_id)
    pipe.execute()


def get_impressions(post_id):
    r = get_redis()
    val = r.get(IMPRESSION_KEY.format(post_id=post_id))
    return int(val) if val else 0


def pop_impression_post_ids():
    r = get_redis()
    ids = r.smembers(IMPRESSION_FLUSH_KEY)
    if ids:
        r.delete(IMPRESSION_FLUSH_KEY)
    return {int(i) for i in ids}


def flush_impressions(post_ids=None):
    r = get_redis()
    from django.db import models
    from posts.models import Post, PostImpression
    ids = post_ids or pop_impression_post_ids()
    if not ids:
        return 0
    pipe = r.pipeline()
    for pid in ids:
        pipe.get(IMPRESSION_KEY.format(post_id=pid))
        pipe.delete(IMPRESSION_KEY.format(post_id=pid))
    results = pipe.execute()
    results = [results[i] for i in range(0, len(results), 2)]
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
    r = get_redis()
    liked_by_key = LIKED_BY_KEY.format(post_id=post_id)
    added = r.sadd(liked_by_key, user_id)
    if added:
        pipe = r.pipeline()
        pipe.incr(LIKES_COUNT_KEY.format(post_id=post_id))
        pipe.expire(liked_by_key, 86400)
        pipe.expire(LIKES_COUNT_KEY.format(post_id=post_id), 86400)
        pipe.sadd(LIKE_FLUSH_KEY, post_id)
        pipe.execute()
    return bool(added)


def unlike_post(post_id, user_id):
    r = get_redis()
    liked_by_key = LIKED_BY_KEY.format(post_id=post_id)
    removed = r.srem(liked_by_key, user_id)
    if removed:
        pipe = r.pipeline()
        pipe.decr(LIKES_COUNT_KEY.format(post_id=post_id))
        pipe.sadd(LIKE_FLUSH_KEY, post_id)
        pipe.execute()
    return bool(removed)


def is_liked(post_id, user_id):
    r = get_redis()
    return r.sismember(LIKED_BY_KEY.format(post_id=post_id), user_id)


def get_likes_count(post_id):
    r = get_redis()
    val = r.get(LIKES_COUNT_KEY.format(post_id=post_id))
    if val is not None:
        return int(val)
    return None


def pop_like_post_ids():
    r = get_redis()
    ids = r.smembers(LIKE_FLUSH_KEY)
    if ids:
        r.delete(LIKE_FLUSH_KEY)
    return {int(i) for i in ids}


def flush_likes(post_ids=None):
    r = get_redis()
    from django.db import models
    from posts.models import Post
    ids = post_ids or pop_like_post_ids()
    if not ids:
        return 0
    pipe = r.pipeline()
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
