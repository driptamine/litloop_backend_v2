from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from artists.models import Artist
from litloop_project.serializers_no_drf import (
    serialize_artist, paginate_queryset, get_paginated_response
)

def artist_list_view(request):
    queryset = Artist.objects.all()
    items, paginator = paginate_queryset(queryset, request)
    response_data = get_paginated_response(items, paginator, serialize_artist, request)
    return JsonResponse(response_data)

def artist_pagination_view(request):
    queryset = Artist.objects.all()
    items, paginator = paginate_queryset(queryset, request, page_size=10)
    data = [serialize_artist(item, request) for item in items]
    payload = {
        'return_code': '0000',
        'return_message': 'Success',
        'artists': data,
        'total': paginator.count,
        'num_pages': paginator.num_pages,
        'current_page': items.number,
    }
    return JsonResponse(payload)

def artist_all_view(request):
    queryset = Artist.objects.all()
    data = [serialize_artist(item, request) for item in queryset]
    payload = {
        'return_code': '0000',
        'return_message': 'Success',
        'artists': data
    }
    return JsonResponse(payload)

def search_artist_view(request):
    term = request.GET.get('q', None)
    if not term:
        return JsonResponse({"error": "Query parameter 'q' is required"}, status=400)
    
    queryset = Artist.objects.filter(name__icontains=term)
    data = [serialize_artist(item, request) for item in queryset]
    return JsonResponse({'items': data})

def artist_detail_view(request, artist_uri):
    artist = get_object_or_404(Artist, artist_uri=artist_uri)
    return JsonResponse(serialize_artist(artist, request))

def artist_albums_view(request, artist_uri):
    artist = get_object_or_404(Artist, artist_uri=artist_uri)
    # The original serializer included albums in ArtistSerializer
    return JsonResponse(serialize_artist(artist, request))
