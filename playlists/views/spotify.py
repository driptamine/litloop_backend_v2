from django.http import JsonResponse, HttpResponseBadRequest
from litloop_project.utils.spotipy_util import get_spotify_client
import logging

logger = logging.getLogger(__name__)

def get_sp():
    try:
        return get_spotify_client()
    except Exception as e:
        logger.error(f"Failed to initialize Spotify client: {e}")
        return None

def playlist_detail(request, playlist_uri):
    if request.method != "GET":
        return HttpResponseBadRequest("Only GET is allowed")
    
    sp = get_sp()
    if not sp:
        return JsonResponse({"error": "Spotify client not configured"}, status=503)

    try:
        results = sp.playlist(playlist_uri)
        return JsonResponse(results)
    except Exception as e:
        logger.error(f"Spotify API Error in playlist_detail: {e}")
        return JsonResponse({"error": str(e)}, status=500)


def playlist_offset(request, playlist_uri):
    if request.method != "GET":
        return HttpResponseBadRequest("Only GET is allowed")

    offset = request.GET.get('offset', 0)
    limit = request.GET.get('limit', 100)

    try:
        offset = int(offset)
        limit = int(limit)
    except ValueError:
        return HttpResponseBadRequest("Offset and limit must be integers")

    sp = get_sp()
    if not sp:
        return JsonResponse({"error": "Spotify client not configured"}, status=503)

    try:
        results = sp.playlist_tracks(playlist_uri, offset=offset, limit=limit)
        return JsonResponse(results)
    except Exception as e:
        logger.error(f"Spotify API Error in playlist_offset: {e}")
        return JsonResponse({"error": str(e)}, status=500)
