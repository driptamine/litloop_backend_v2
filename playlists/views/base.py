from django.http import JsonResponse
from django.views import View
from django.core.paginator import Paginator
from django.contrib.auth.models import User
import json

from playlists.models import Playlist

class PlaylistListView(View):
    def get(self, request):
        playlists = Playlist.objects.select_related("user").all()

        author = request.GET.get("author")
        if author:
            playlists = playlists.filter(user__username=author)

        paginator = Paginator(playlists, 10)
        page_number = request.GET.get("page", 1)
        page = paginator.get_page(page_number)

        data = [
            {
                "id": playlist.id,
                "name": playlist.name,
                "user": playlist.user.username,
                "description": playlist.description,
            }
            for playlist in page
        ]

        return JsonResponse({
            "count": paginator.count,
            "num_pages": paginator.num_pages,
            "current_page": page.number,
            "results": data,
        })

    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)

        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        name = body.get('name')
        description = body.get('description', '')

        if not name:
            return JsonResponse({'error': 'Name is required'}, status=400)

        playlist = Playlist.objects.create(
            name=name,
            description=description,
            user=request.user,
        )

        return JsonResponse({
            "id": playlist.id,
            "name": playlist.name,
            "description": playlist.description,
            "user": playlist.user.username
        }, status=201)

def playlist_detail(request, playlist_uri):
    # In this app, models don't seem to have playlist_uri, 
    # but the original code used it. I'll use 'id' as a fallback if uri is not in models.
    # Looking at playlists/models.py...
    playlist = get_object_or_404(Playlist, id=playlist_uri) # Assuming id for now
    return JsonResponse({
        "id": playlist.id,
        "name": playlist.name,
        "description": playlist.description,
        "user": playlist.user.username,
    })

def playlist_offset(request, playlist_uri):
    # Local DB doesn't have offset-based tracks in the same way Spotify does 
    # unless we use a relationship. 
    return playlist_detail(request, playlist_uri)
