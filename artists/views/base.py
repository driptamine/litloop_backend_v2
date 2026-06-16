from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import RetrieveAPIView

from artists.models import Artist
from artists.serializers import ArtistListSerializer, ArtistSerializer
from albums.pagination import CustomPagination

class ArtistListAPIView(ListAPIView):
    queryset = Artist.objects.all()
    serializer_class = ArtistListSerializer

from rest_framework.generics import GenericAPIView
from albums.pagination import CustomPagination

class ArtistPaginationAPIView(GenericAPIView):
    serializer_class = ArtistSerializer
    queryset = Artist.objects.all()
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
            'artists': data
        }
        return Response(payload)

class ArtistAllAPIView(APIView):
    def get(self, request):
        queryset = Artist.objects.all()
        serializer = ArtistSerializer(queryset, many=True, context={'request': request})
        payload = {
            'return_code': '0000',
            'return_message': 'Success',
            'artists': serializer.data
        }
        return Response(payload)

class SearchArtistAPIView(APIView):
    def get(self, request):
        term = request.query_params.get('q', None)
        if not term:
            return Response({"error": "Query parameter 'q' is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = Artist.objects.filter(name__icontains=term)
        serializer = ArtistSerializer(queryset, many=True, context={'request': request})
        return Response({'items': serializer.data})

class ArtistDetailAPIView(RetrieveAPIView):
    serializer_class = ArtistSerializer
    queryset = Artist.objects.all()
    lookup_field = 'artist_uri'

class ArtistAlbumsAPIView(RetrieveAPIView):
    serializer_class = ArtistSerializer
    queryset = Artist.objects.all()
    lookup_field = 'artist_uri'
