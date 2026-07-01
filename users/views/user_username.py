from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from users.models import User
from posts.models import Post
from movies.models import WatchlistItem
from users.auth_utils import jwt_required
from tracks.views.base_no_drf import user_tracks_view
from photos.models import Photo, PhotoAlbum
from videos.models import Video
from litloop_project.r2_storage import r2_url
from litloop_project.serializers_no_drf import paginate_queryset

def user_username_detail_api(request, username):
    user = get_object_or_404(User, username=username)
    
    data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'avatar': user.avatar,
        'is_verified': user.is_verified,
        'is_active': user.is_active,
        'is_staff': user.is_staff,
        'created_at': user.created_at.isoformat(),
        'updated_at': user.updated_at.isoformat(),
    }
    
    return JsonResponse(data)

def user_username_posts_api(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user).order_by('-created_at')
    
    post_data = []
    for post in posts:
        post_data.append({
            'id': post.id,
            'title': post.title,
            'description': post.description,
            'friendly_id': post.friendly_id,
            'likes_count': post.likes_count,
            'dislikes_count': post.dislikes_count,
            'views_count': post.views_count,
            'created_at': post.created_at.isoformat(),
            'updated_at': post.updated_at.isoformat(),
        })
    
    data = {
        'username': user.username,
        'count': posts.count(),
        'results': post_data
    }
    
    return JsonResponse(data)

@jwt_required
def user_username_watchlist_api(request, username):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    user = get_object_or_404(User, username=username)

    # Check: Only allow the authenticated user to see their own watchlist
    if request.user.id != user.id:
        return JsonResponse({"error": "Forbidden"}, status=403)

    # Pagination
    try:
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 10))
    except ValueError:
        return JsonResponse({"error": "Invalid pagination parameters"}, status=400)

    if page < 1 or per_page < 1:
        return JsonResponse({"error": "Page and per_page must be positive integers."}, status=400)

    watchlist_qs = (
        WatchlistItem.objects.filter(user=user)
        .select_related('movie')
        .order_by('-movie__created_at')
    )

    total_items = watchlist_qs.count()
    total_pages = (total_items + per_page - 1) // per_page

    start = (page - 1) * per_page
    end = start + per_page

    watchlist_page = watchlist_qs[start:end]

    watchlist_data = [
        {
            "movie_id": item.movie.id,
            "title": item.movie.title,
            "imdb_created_at": item.movie.created_at.isoformat() if item.movie.created_at else None
        }
        for item in watchlist_page
    ]

    return JsonResponse({
        "username": user.username,
        "page": page,
        "per_page": per_page,
        "total_items": total_items,
        "total_pages": total_pages,
        "watchlist": watchlist_data
    })

def user_username_tracks_api(request, username):
    return user_tracks_view(request, username)


@jwt_required
def user_username_photos_api(request, username):
    user = get_object_or_404(User, username=username)
    queryset = Photo.objects.filter(user=user).order_by('-id')
    items, paginator = paginate_queryset(queryset, request, page_size=30)

    data = []
    for photo in items:
        url = r2_url(photo.gcs_key) or r2_url(photo.s3_key)
        data.append({
            'id': photo.id,
            'pk': photo.pk,
            'gcs_url': url,
            'image': url,
            'url': url,
            'file_path': url,
            'name': photo.title or photo.filename or f'Photo {photo.id}',
            'title': photo.title or photo.filename or f'Photo {photo.id}',
        })

    return JsonResponse({
        'photos': data,
        'total': paginator.count,
        'num_pages': paginator.num_pages,
        'current_page': items.number,
    })


@jwt_required
def user_username_albums_api(request, username):
    user = get_object_or_404(User, username=username)
    queryset = PhotoAlbum.objects.filter(user=user).order_by('-add_date')
    items, paginator = paginate_queryset(queryset, request, page_size=30)

    data = []
    for album in items:
        first_item = album.photoalbumitem_set.first()
        thumbnail_url = r2_url(first_item.photo.gcs_key if first_item else None)

        data.append({
            'id': album.id,
            'title': album.title,
            'description': album.description,
            'friendly_token': album.friendly_token,
            'thumbnail_url': thumbnail_url,
            'photo_count': album.photo.count(),
            'add_date': album.add_date,
        })

    return JsonResponse({
        'albums': data,
        'total': paginator.count,
        'num_pages': paginator.num_pages,
        'current_page': items.number,
    })


@jwt_required
def user_username_videos_api(request, username):
    user = get_object_or_404(User, username=username)
    queryset = Video.objects.filter(user=user).order_by('-id')
    items, paginator = paginate_queryset(queryset, request, page_size=30)

    data = []
    for video in items:
        gcs_url = r2_url(video.gcs_key)
        thumb = video.thumbnail
        data.append({
            'id': video.id,
            'pk': video.pk,
            'video_id': video.id,
            'gcs_url': gcs_url,
            'url': gcs_url,
            'file': gcs_url,
            'file_path': video.gcs_key,
            'thumbnail': thumb,
            'thumbNail': thumb,
            'title': video.title or f'Video {video.id}',
            'name': video.title or f'Video {video.id}',
        })

    return JsonResponse({
        'videos': data,
        'total': paginator.count,
        'num_pages': paginator.num_pages,
        'current_page': items.number,
    })
