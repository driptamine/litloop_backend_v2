import redis

_redis_client = None

def get_redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
    return _redis_client

IMPRESSION_KEY = 'movie:{movie_id}:impressions'
LIKES_COUNT_KEY = 'movie:{movie_id}:likes_count'
LIKED_BY_KEY = 'movie:{movie_id}:liked_by'
IMPRESSION_FLUSH_KEY = 'movie:impressions:pending'
LIKE_FLUSH_KEY = 'movie:likes:pending'


def record_impression(movie_id):
    r = get_redis()
    key = IMPRESSION_KEY.format(movie_id=movie_id)
    pipe = r.pipeline()
    pipe.incr(key)
    pipe.expire(key, 86400)
    pipe.sadd(IMPRESSION_FLUSH_KEY, movie_id)
    pipe.execute()


def get_impressions(movie_id):
    r = get_redis()
    val = r.get(IMPRESSION_KEY.format(movie_id=movie_id))
    return int(val) if val else 0


def pop_impression_movie_ids():
    r = get_redis()
    ids = r.smembers(IMPRESSION_FLUSH_KEY)
    if ids:
        r.delete(IMPRESSION_FLUSH_KEY)
    return {int(i) for i in ids}


def flush_impressions(movie_ids=None):
    r = get_redis()
    from django.db import models
    from movies.models import Movie, MovieImpression
    ids = movie_ids or pop_impression_movie_ids()
    if not ids:
        return 0
    pipe = r.pipeline()
    for mid in ids:
        pipe.getdel(IMPRESSION_KEY.format(movie_id=mid))
    results = pipe.execute()
    recorded = 0
    for mid, raw in zip(ids, results):
        count = int(raw) if raw else 0
        if count <= 0:
            continue
        try:
            movie = Movie.objects.get(id=mid)
            MovieImpression.objects.bulk_create([
                MovieImpression(movie=movie, user=None) for _ in range(count)
            ])
            Movie.objects.filter(id=mid).update(impressions_count=models.F('impressions_count') + count)
            recorded += count
        except Movie.DoesNotExist:
            continue
    return recorded


def like_movie(movie_id, user_id):
    r = get_redis()
    liked_by_key = LIKED_BY_KEY.format(movie_id=movie_id)
    added = r.sadd(liked_by_key, user_id)
    if added:
        pipe = r.pipeline()
        pipe.incr(LIKES_COUNT_KEY.format(movie_id=movie_id))
        pipe.expire(liked_by_key, 86400)
        pipe.expire(LIKES_COUNT_KEY.format(movie_id=movie_id), 86400)
        pipe.sadd(LIKE_FLUSH_KEY, movie_id)
        pipe.execute()
    return bool(added)


def unlike_movie(movie_id, user_id):
    r = get_redis()
    liked_by_key = LIKED_BY_KEY.format(movie_id=movie_id)
    removed = r.srem(liked_by_key, user_id)
    if removed:
        pipe = r.pipeline()
        pipe.decr(LIKES_COUNT_KEY.format(movie_id=movie_id))
        pipe.sadd(LIKE_FLUSH_KEY, movie_id)
        pipe.execute()
    return bool(removed)


def is_liked(movie_id, user_id):
    r = get_redis()
    return r.sismember(LIKED_BY_KEY.format(movie_id=movie_id), user_id)


def get_likes_count(movie_id):
    r = get_redis()
    val = r.get(LIKES_COUNT_KEY.format(movie_id=movie_id))
    if val is not None:
        return int(val)
    return None


def pop_like_movie_ids():
    r = get_redis()
    ids = r.smembers(LIKE_FLUSH_KEY)
    if ids:
        r.delete(LIKE_FLUSH_KEY)
    return {int(i) for i in ids}


def flush_likes(movie_ids=None):
    r = get_redis()
    from django.db import models
    from movies.models import Movie
    ids = movie_ids or pop_like_movie_ids()
    if not ids:
        return 0
    pipe = r.pipeline()
    liked_by_keys = [LIKED_BY_KEY.format(movie_id=mid) for mid in ids]
    for key in liked_by_keys:
        pipe.scard(key)
    like_counts = pipe.execute()
    synced = 0
    for mid, scard in zip(ids, like_counts):
        count = int(scard) if scard else 0
        Movie.objects.filter(id=mid).update(likes_count=count)
        synced += 1
    return synced
