from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from rest_framework import status, permissions
from rest_framework.generics import ListAPIView, RetrieveAPIView, GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination

from albums.models import Album
from albums.serializers import AlbumsSerializer
from albums.pagination import CustomPagination

# NOTE: Like model import is missing in original views.py, 
# likely causing a NameError and 500. 
# Attempting to locate or stub if necessary.
# Given LIKES_MODELS in settings, it might be using a generic app.
# For now, I will comment out the Like logic or try to find it.

class PagePagination(LimitOffsetPagination):
    default_limit = 2
    max_limit = 50
    limit_query_param = 'limit'
    offset_query_param = 'offset'

class AlbumListAPIView(ListAPIView):
    queryset = Album.objects.all()
    pagination_class = PagePagination
    serializer_class = AlbumsSerializer

class AlbumAPIView(RetrieveAPIView):
    queryset = Album.objects.all()
    serializer_class = AlbumsSerializer
    lookup_field = 'id'

class AlbumLikeAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated, )
    queryset = Album.objects.all()
    serializer_class = AlbumsSerializer
    lookup_field = 'id'

    def put(self, request, id):
        user = self.request.user
        al = get_object_or_404(Album, id=id)
        
        # content_type = ContentType.objects.get_for_model(Album)
        # BUG: 'Like' is not defined. 
        # This was likely one of the causes of the 500 error.
        
        # Placeholder for like logic until Like model is found
        return Response({"detail": "Like functionality pending model verification"}, status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, id, format=None):
        snippet = get_object_or_404(Album, id=id)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class TestAlbumLikeAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated, )
    queryset = Album.objects.all()
    serializer_class = AlbumsSerializer
    lookup_field = 'album_uri'

    def put(self, request, album_uri):
        user = self.request.user
        al = get_object_or_404(Album, album_uri=album_uri)
        
        # BUG: 'Like' is not defined.
        return Response({"detail": "Like functionality pending model verification"}, status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, album_uri, format=None):
        snippet = get_object_or_404(Album, album_uri=album_uri)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AlbumPaginationAPIView(GenericAPIView):
    serializer_class = AlbumsSerializer
    queryset = Album.objects.all()
    pagination_class = CustomPagination

    def get(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            data = result.data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
        payload = {
            'return_code': '0000',
            'return_message': 'Success',
            'albums': data
        }
        return Response(payload)

class AlbumAllAPIView(APIView):
    def get(self, request):
        queryset = Album.objects.all()
        serializer = AlbumsSerializer(queryset, many=True, context={'request': request})
        payload = {
            'return_code': '0000',
            'return_message': 'Success',
            'albums': serializer.data
        }
        return Response(payload)

class SearchAlbumAPIView(APIView):
    def get(self, request):
        term = request.query_params.get('q', None)
        if not term:
            return Response({"error": "Query parameter 'q' is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = Album.objects.filter(name__icontains=term)
        serializer = AlbumsSerializer(queryset, many=True, context={'request': request})
        return Response({'items': serializer.data})

class AlbumDetailAPIView(RetrieveAPIView):
    serializer_class = AlbumsSerializer
    queryset = Album.objects.all()
    lookup_field = 'album_uri'

class FeedAPIView(ListAPIView):
    serializer_class = AlbumsSerializer
    queryset = Album.objects.all().order_by('-created_at')
    pagination_class = PagePagination
