from django.shortcuts import render, get_object_or_404
from django.db import IntegrityError
from django.conf import settings

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import pprint

from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveAPIView,
    ListAPIView,
    CreateAPIView,
    GenericAPIView,
)
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from posts.renderers import PostRenderer
# from tracks.models import Track
# Create your views here.
from .models import Track
from .serializers import TrackSerializer, TrackListSerializer
from tracks.pagination import CustomPagination

from litloop_project.utils.spotipy_util import get_spotify_client

sp = get_spotify_client()

class TrackListAPIView(ListAPIView):
    queryset = Track.objects.all()
    serializer_class = TrackListSerializer

class SearchTrackAPIView(APIView):
    # lookup_field = 'track_uri'
    renderer_classes = (PostRenderer,)

    def get(self, request):
        term = self.request.query_params.get('q', None)


        search_result = sp.search(term, limit=10, type='track')
        # res = PostSerializer(search_result)
        return Response(search_result.get('tracks'))
        # return Response(search_result)
        # return Response(res)



SPOTIPY_CLIENT_ID = settings.SPOTIPY_CLIENT_ID
SPOTIPY_CLIENT_SECRET = settings.SPOTIPY_CLIENT_SECRET

class TrackDetailAPIView(RetrieveAPIView):
    # serializer_class = PostSerializer
    lookup_field = 'track_uri'

    def get(self, request, track_uri):
        
        track_info = sp.track(track_uri)

        return Response(track_info)




class TrackGetOrCreateAPIView(RetrieveAPIView):
    # serializer_class = PostSerializer
    lookup_field = 'track_uri'

    def get(self, request, track_uri):
        SPOTIPY_CLIENT_ID = "c57cfe40c3a640449c4766ee61ec9d59"
        SPOTIPY_CLIENT_SECRET = "8c5ae0b0d9df47c8bae2804fe8e03cfa"

        sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=SPOTIPY_CLIENT_ID,
                client_secret=SPOTIPY_CLIENT_SECRET
            )
        )

        from artists.models import Artist
        from albums.models import Album
        from images.models import Image

        track_data = sp.track(track_uri)

        album_uri = track_data['album']['id']
        album_data = sp.album(album_uri)
        album = Album.create(**album_data)
        # spotify_album.delay(**album_data)

        track = Track.create(**track_data)
        # spotify_track.delay(**track_data)

        for artist_data in track_data['artists']:
            artist_uri = artist_data['id']
            artist_data = sp.artist(artist_uri)
            Artist.create(**artist_data)
            # spotify_artist.delay(**artist_data)



        snippet = Track.objects.get(track_uri=track_uri)
        serializer = TrackSerializer(snippet, context={'request': self.request})
        return Response(serializer.data)
        # return Response(track_info)

class TrackPaginationAPIView(GenericAPIView):
    serializer_class = TrackSerializer
    queryset = Track.objects.all()
    pagination_class = CustomPagination

    def get(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            data = result.data # pagination data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
        payload = {
            'return_code': '0000',
            'return_message': 'Success',
            'tracks': data
        }
        return Response(payload)
