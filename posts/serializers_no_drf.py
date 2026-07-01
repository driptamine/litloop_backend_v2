import json
from posts.models import Post, PostPhoto, PostVideo, PostTrack, PostPlaylist, PostLike
from photos.models import Photo
from videos.models import Video
from tracks.models import Track
from playlists.models import Playlist
from litloop_project.r2_storage import r2_url

def serialize_post(post, request=None):
    cloudfront_domain = 'https://dgsmmq1mgfewt.cloudfront.net/'

    photos_data = post.photos.all().values('id', 's3_key', 'gcs_key', 'title')
    videos_data = post.videos.all().values('id', 's3_key', 'gcs_key', 'title', 'thumbnail')
    tracks = post.tracks.all().prefetch_related('artists')
    playlists_data = post.playlists.all().values('id', 'title')

    is_liked = False
    if request and hasattr(request, 'user') and request.user.is_authenticated:
        is_liked = PostLike.objects.filter(post=post, user=request.user).exists()

    return {
        'id': post.id,
        'title': post.title,
        'description': post.description,
        'friendly_id': post.friendly_id,
        'author': {
            'id': post.author.id,
            'username': post.author.username,
            'avatar': post.author.avatar,
        } if post.author else None,
        'is_liked': is_liked,
        'likes_count': post.likes_count,
        'dislikes_count': post.dislikes_count,
        'views_count': post.views_count,
        'impressions_count': post.impressions_count,
        'created_at': post.created_at.isoformat() if post.created_at else None,
        'updated_at': post.updated_at.isoformat() if post.updated_at else None,
        'photos': [
            {
                'id': p['id'],
                'url': r2_url(p.get('gcs_key')) or r2_url(p.get('s3_key')),
                'gcs_url': r2_url(p.get('gcs_key')),
                'gcs_key': p['gcs_key'],
                'title': p['title']
            } for p in photos_data
        ],
        'videos': [
            {
                'id': v['id'],
                'url': r2_url(v.get('gcs_key')) or r2_url(v.get('s3_key')),
                'gcs_url': r2_url(v.get('gcs_key')),
                'gcs_key': v['gcs_key'],
                'thumbnail_url': r2_url(v.get('thumbnail')),
                'title': v['title']
            } for v in videos_data
        ],
        'tracks': [
            {
                'id': t.id,
                'url': r2_url(t.gcs_key) or r2_url(t.s3_key),
                'gcs_url': r2_url(t.gcs_key),
                'gcs_key': t.gcs_key,
                'name': t.name,
                'artists': [{'id': a.artist_uri, 'name': a.name} for a in t.artists.all()]
            } for t in tracks
        ],
        'playlists': [
            {
                'id': pl['id'],
                'title': pl['title']
            } for pl in playlists_data
        ],
    }

def handle_media_linking(post, data, clear_existing=False):
    if 'photo_ids' in data:
        if clear_existing:
            PostPhoto.objects.filter(post=post).delete()
        for i, pid in enumerate(data.get('photo_ids', [])):
            try:
                photo = Photo.objects.get(id=pid)
                PostPhoto.objects.get_or_create(post=post, photo=photo, defaults={'order': i+1})
            except Photo.DoesNotExist:
                continue

    if 'video_ids' in data:
        if clear_existing:
            PostVideo.objects.filter(post=post).delete()
        for i, vid in enumerate(data.get('video_ids', [])):
            try:
                video = Video.objects.get(id=vid)
                PostVideo.objects.get_or_create(post=post, video=video, defaults={'order': i+1})
            except Video.DoesNotExist:
                continue

    if 'track_ids' in data:
        if clear_existing:
            PostTrack.objects.filter(post=post).delete()
        for i, tid in enumerate(data.get('track_ids', [])):
            try:
                track = Track.objects.get(id=tid)
                PostTrack.objects.get_or_create(post=post, track=track, defaults={'order': i+1})
            except Track.DoesNotExist:
                continue

    if 'playlist_ids' in data:
        if clear_existing:
            PostPlaylist.objects.filter(post=post).delete()
        for i, plid in enumerate(data.get('playlist_ids', [])):
            try:
                playlist = Playlist.objects.get(id=plid)
                PostPlaylist.objects.get_or_create(post=post, playlist=playlist, defaults={'order': i+1})
            except Playlist.DoesNotExist:
                continue
