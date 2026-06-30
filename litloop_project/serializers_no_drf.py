from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings

def paginate_queryset(queryset, request, page_size=10):
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, page_size)
    
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)
        
    return items, paginator

def get_paginated_response(items, paginator, serializer_func, request=None):
    return {
        'total': paginator.count,
        'num_pages': paginator.num_pages,
        'current_page': items.number,
        'items': [serializer_func(item, request) for item in items],
        'next': items.next_page_number() if items.has_next() else None,
        'previous': items.previous_page_number() if items.has_previous() else None,
    }

def serialize_user(user, request=None):
    if not user:
        return None
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'avatar': user.avatar,
    }

def serialize_image(image, request=None):
    if not image:
        return None
    return {
        'url': image.url,
        'height': image.height,
        'width': image.width,
    }

def serialize_artist(artist, request=None):
    if not artist:
        return None
    return {
        'id': artist.artist_uri,
        'name': artist.name,
        'artist_uri': artist.artist_uri,
        'images': [serialize_image(img, request) for img in artist.images.all()] if hasattr(artist, 'images') else [],
    }

def serialize_track(track, request=None):
    if not track:
        return None
    
    gcs_url = None
    if track.gcs_key:
        gcs_url = f"https://storage.googleapis.com/{settings.GCS_BUCKET_NAME}/{track.gcs_key}"
        
    return {
        'id': track.track_uri,
        'pk': track.pk,
        'name': track.name,
        'track_uri': track.track_uri,
        'track_number': track.track_number,
        'user': serialize_user(track.user, request),
        'artists': [serialize_artist(a, request) for a in track.artists.all()],
        'gcs_url': gcs_url,
        's3_key': getattr(track, 's3_key', None),
        'release_date': track.release_date.isoformat() if getattr(track, 'release_date', None) else None,
    }

def serialize_album(album, request=None):
    if not album:
        return None
    
    return {
        'id': album.album_uri,
        'pk': album.pk,
        'name': album.name,
        'album_uri': album.album_uri,
        'artists': [serialize_artist(a, request) for a in album.artists.all()],
        'images': [serialize_image(img, request) for img in album.images.all()],
        'created_at': album.created_at.isoformat() if getattr(album, 'created_at', None) else None,
        'updated_at': album.updated_at.isoformat() if getattr(album, 'updated_at', None) else None,
    }

def serialize_comment(comment, request=None):
    if not comment:
        return None
    return {
        'uid': comment.uid,
        'add_date': comment.add_date.isoformat() if comment.add_date else None,
        'text': comment.text,
        'parent': comment.parent.uid if comment.parent else None,
        'author_name': comment.user.name if comment.user else None,
        'author_thumbnail_url': comment.user.thumbnail_url if comment.user else None,
        'author_profile': comment.user.get_absolute_url() if comment.user else None,
        'media_url': comment.media_url,
    }

def serialize_imdb_movie(movie, request=None):
    if not movie:
        return None
    return {
        'id': movie.id,
        'imdb_id': movie.imdb_id,
        'title': movie.title,
        'url': movie.url,
        'title_type': movie.title_type,
        'imdb_rating': movie.imdb_rating,
        'runtime_minutes': movie.runtime_minutes,
        'year': movie.year,
        'genres': movie.genres,
        'num_votes': movie.num_votes,
        'release_date': movie.release_date.isoformat() if movie.release_date else None,
        'directors': movie.directors,
        'description': movie.description,
        'created_at': movie.created_at.isoformat() if movie.created_at else None,
        'modified_at': movie.modified_at.isoformat() if movie.modified_at else None,
    }

def serialize_movie(movie, request=None):
    if not movie:
        return None
    return {
        'id': movie.id,
        'tmdb_id': movie.tmdb_id,
        'imdb_id': movie.imdb_id,
        'title': movie.title,
        'description': movie.description,
        'movie_file': movie.movie_file,
        'poster': movie.poster,
        'likes_count': movie.likes_count,
        'dislikes_count': movie.dislikes_count,
        'views_count': movie.views_count,
        'impressions_count': movie.impressions_count,
    }
