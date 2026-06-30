import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from memes.models import Meme


def memes_list_view(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        resp = requests.get('https://meme-api.com/gimme/26', timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        return JsonResponse({'error': str(e)}, status=502)

    raw_memes = data.get('memes', [])
    for item in raw_memes:
        Meme.objects.get_or_create(
            meme_id=item.get('postLink', str(item.get('title', ''))),
            defaults={
                'title': item.get('title', ''),
                'url': item.get('url', ''),
                'post_link': item.get('postLink', ''),
                'subreddit': item.get('subreddit', ''),
                'author': item.get('author', ''),
                'nsfw': item.get('nsfw', False),
                'spoiler': item.get('spoiler', False),
                'ups': item.get('ups', 0),
                'preview': item.get('preview', ''),
            }
        )

    memes_data = [{
        'id': m.id,
        'title': m.title,
        'url': m.url,
        'post_link': m.post_link,
        'subreddit': m.subreddit,
        'author': m.author,
        'nsfw': m.nsfw,
        'ups': m.ups,
        'preview': m.preview,
    } for m in Meme.objects.filter(
        meme_id__in=[item.get('postLink', str(item.get('title', ''))) for item in raw_memes]
    )]

    return JsonResponse(memes_data, safe=False)


def memes_list_db_view(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    memes = Meme.objects.all().order_by('-created_at')[:50]
    data = [{
        'id': m.id,
        'title': m.title,
        'url': m.url,
        'post_link': m.post_link,
        'subreddit': m.subreddit,
        'author': m.author,
        'nsfw': m.nsfw,
        'ups': m.ups,
        'preview': m.preview,
        'likes': m.liked_by.count(),
    } for m in memes]
    return JsonResponse(data, safe=False)
