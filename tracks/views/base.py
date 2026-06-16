from rest_framework.generics import ListAPIView, GenericAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from tracks.models import Track
from tracks.serializers import TrackListSerializer, TrackSerializer
from tracks.pagination import CustomPagination

class TrackListAPIView(ListAPIView):
    queryset = Track.objects.all().order_by('-id')
    serializer_class = TrackListSerializer

class TrackPaginationAPIView(GenericAPIView):
    serializer_class = TrackSerializer
    queryset = Track.objects.all().order_by('-id')
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
            'tracks': data
        }
        return Response(payload)

class TrackAllAPIView(APIView):
    def get(self, request):
        queryset = Track.objects.all().order_by('-id')
        serializer = TrackListSerializer(queryset, many=True, context={'request': request})
        payload = {
            'return_code': '0000',
            'return_message': 'Success',
            'tracks': serializer.data
        }
        return Response(payload)

class SearchTrackAPIView(APIView):
    def get(self, request):
        term = request.query_params.get('q', None)
        if not term:
            return Response({"error": "Query parameter 'q' is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = Track.objects.filter(name__icontains=term)
        serializer = TrackSerializer(queryset, many=True, context={'request': request})
        return Response({'items': serializer.data})

class TrackDetailAPIView(RetrieveAPIView):
    serializer_class = TrackSerializer
    queryset = Track.objects.all()
    lookup_field = 'track_uri'
