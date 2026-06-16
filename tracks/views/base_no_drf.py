import json
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from tracks.models import Track
from users.auth_utils import jwt_required_testable
from litloop_project.serializers_no_drf import (
    serialize_track, paginate_queryset, get_paginated_response
)

@csrf_exempt
@jwt_required_testable
def track_update_view(request, track_uri=None, pk=None):
    if request.method not in ['PUT', 'PATCH']:
        return JsonResponse({'error': f'Method {request.method} not allowed'}, status=405)

    if pk:
        track = get_object_or_404(Track, pk=pk)
    else:
        track = get_object_or_404(Track, track_uri=track_uri)

    # Permission check: Only the user who uploaded the track (or staff) can update it
    if track.user != request.user and not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if 'name' in data:
        track.name = data['name']
    if 'track_number' in data:
        track.track_number = data['track_number']
    if 'status' in data:
        track.status = data['status']
    if 'release_date' in data:
        track.release_date = data['release_date']

    if 'album_uri' in data:
        from albums.models import Album
        try:
            album = Album.objects.get(album_uri=data['album_uri'])
            track.album = album
        except Album.DoesNotExist:
            pass

    if 'artist_uris' in data:
        from artists.models import Artist
        artists = Artist.objects.filter(artist_uri__in=data['artist_uris'])
        track.artists.set(artists)

    # Support 'artist_names' or simply 'artists' from the client
    artist_names = data.get('artist_names') or data.get('artists')
    if artist_names:
        from artists.models import Artist
        
        # 1. Handle String input (with semicolon support for names with commas)
        if isinstance(artist_names, str):
            if ';' in artist_names:
                artist_names = [name.strip() for name in artist_names.split(';') if name.strip()]
            else:
                # Fallback to comma, but advise using a list or semicolon for safety
                artist_names = [name.strip() for name in artist_names.split(',') if name.strip()]
        
        # 2. At this point artist_names is a list (either sent as one or split from a string)
        artist_objs = []
        for name in artist_names:
            artist, created = Artist.objects.get_or_create(
                name=name,
                defaults={'artist_uri': f"local-{name.lower().replace(' ', '-')}"}
            )
            artist_objs.append(artist)
        track.artists.set(artist_objs)
    
    track.save()

    return JsonResponse(serialize_track(track, request))

@csrf_exempt
@jwt_required_testable
def track_delete_view(request, track_uri=None, pk=None):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Only DELETE allowed'}, status=405)

    if pk:
        track = get_object_or_404(Track, pk=pk)
    else:
        track = get_object_or_404(Track, track_uri=track_uri)

    if track.user != request.user and not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    track.delete()
    return JsonResponse({'message': 'Track deleted'}, status=204)

def track_list_view(request):
    queryset = Track.objects.all().select_related('user').prefetch_related('artists').order_by('-id')
    items, paginator = paginate_queryset(queryset, request)
    response_data = get_paginated_response(items, paginator, serialize_track, request)
    return JsonResponse(response_data)

def track_pagination_view(request):
    queryset = Track.objects.all().select_related('user').prefetch_related('artists').order_by('-id')
    items, paginator = paginate_queryset(queryset, request, page_size=10)
    data = [serialize_track(item, request) for item in items]
    payload = {
        'return_code': '0000',
        'return_message': 'Success',
        'tracks': data,
        'total': paginator.count,
        'num_pages': paginator.num_pages,
        'current_page': items.number,
    }
    return JsonResponse(payload)

def track_all_view(request):
    queryset = Track.objects.all().select_related('user').prefetch_related('artists').order_by('-id')
    data = [serialize_track(item, request) for item in queryset]
    payload = {
        'return_code': '0000',
        'return_message': 'Success',
        'tracks': data
    }
    return JsonResponse(payload)

def user_tracks_view(request, username):
    from users.models import User
    user = get_object_or_404(User, username=username)
    queryset = Track.objects.filter(user=user).select_related('user').prefetch_related('artists').order_by('-id')
    
    items, paginator = paginate_queryset(queryset, request, page_size=10)
    data = [serialize_track(item, request) for item in items]
    
    payload = {
        'return_code': '0000',
        'return_message': 'Success',
        'username': user.username,
        'tracks': data,
        'total': paginator.count,
        'num_pages': paginator.num_pages,
        'current_page': items.number,
    }
    return JsonResponse(payload)

def search_track_view(request):
    term = request.GET.get('q', None)
    if not term:
        return JsonResponse({"error": "Query parameter 'q' is required"}, status=400)
    
    queryset = Track.objects.filter(name__icontains=term)
    data = [serialize_track(item, request) for item in queryset]
    return JsonResponse({'items': data})

def track_detail_view(request, track_uri=None, pk=None):
    if pk:
        track = get_object_or_404(Track.objects.select_related('user').prefetch_related('artists'), pk=pk)
    else:
        track = get_object_or_404(Track.objects.select_related('user').prefetch_related('artists'), track_uri=track_uri)
    return JsonResponse(serialize_track(track, request))
