from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from albums.models import Album
from litloop_project.serializers_no_drf import (
    serialize_album, paginate_queryset, get_paginated_response
)
from users.auth_utils import jwt_required_testable

def album_list_view(request):
    queryset = Album.objects.all()
    items, paginator = paginate_queryset(queryset, request, page_size=2)
    response_data = get_paginated_response(items, paginator, serialize_album, request)
    return JsonResponse(response_data)

def album_detail_view(request, id=None, album_uri=None):
    if id:
        album = get_object_or_404(Album, id=id)
    else:
        album = get_object_or_404(Album, album_uri=album_uri)
    return JsonResponse(serialize_album(album, request))

@csrf_exempt
@jwt_required_testable
def album_like_view(request, id=None, album_uri=None):
    if id:
        album = get_object_or_404(Album, id=id)
    else:
        album = get_object_or_404(Album, album_uri=album_uri)

    if request.method == 'PUT':
        # Placeholder for like logic
        return JsonResponse({"detail": "Like functionality pending model verification"}, status=501)
    
    elif request.method == 'DELETE':
        album.delete()
        return JsonResponse({}, status=204)
    
    return JsonResponse({"error": "Method not allowed"}, status=405)

def album_pagination_view(request):
    queryset = Album.objects.all()
    items, paginator = paginate_queryset(queryset, request, page_size=10)
    data = [serialize_album(item, request) for item in items]
    
    payload = {
        'return_code': '0000',
        'return_message': 'Success',
        'albums': data,
        'total': paginator.count,
        'num_pages': paginator.num_pages,
        'current_page': items.number,
    }
    return JsonResponse(payload)

def album_all_view(request):
    queryset = Album.objects.all()
    data = [serialize_album(item, request) for item in queryset]
    payload = {
        'return_code': '0000',
        'return_message': 'Success',
        'albums': data
    }
    return JsonResponse(payload)

def search_album_view(request):
    term = request.GET.get('q', None)
    if not term:
        return JsonResponse({"error": "Query parameter 'q' is required"}, status=400)
    
    queryset = Album.objects.filter(name__icontains=term)
    data = [serialize_album(item, request) for item in queryset]
    return JsonResponse({'items': data})

def feed_view(request):
    queryset = Album.objects.all().order_by('-created_at')
    items, paginator = paginate_queryset(queryset, request, page_size=2)
    response_data = get_paginated_response(items, paginator, serialize_album, request)
    return JsonResponse(response_data)
