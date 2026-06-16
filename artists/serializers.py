from rest_framework import serializers

from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed

# import tracks.models as Track
# from tracks.models import Track
# from artists.models import Artist
# from .models import Album

from django.apps import apps
 
# Track = apps.get_model(app_label='tracks', model_name='Track')
Artist = apps.get_model(app_label='artists', model_name='Artist')
Album = apps.get_model(app_label='albums', model_name='Album')
# Like = apps.get_model(app_label='likes', model_name='Like')
Image = apps.get_model(app_label='images', model_name='Image')


class ArtistsSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = Artist
        fields = [
            'id',
            'name',
            'artist_uri',

        ]

    def get_id(self, obj):

        return obj.artist_uri


class ArtistImagesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = [
            # 'id',
            'url',
            'height',
            'width',

        ]
        # ref_name = "User 1"


class AlbumsSerializer(serializers.ModelSerializer):
    artists = ArtistsSerializer(many=True)
    # tracks = serializers.SerializerMethodField()
    images = ArtistImagesSerializer(many=True)
    is_liked = serializers.SerializerMethodField()
    total_likes = serializers.SerializerMethodField()
    # posts = PostsSerializer(many=True)
    id = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = [
            'id',
            'name',
            # 'tracks',
            'artists',
            # 'images',
            # 'album_id',
            'album_uri',
            'images',
            'is_liked',
            # 'likes_count',
            'total_likes',
            # 'created_at',
            # 'updated_at',
            # 'likes_count',
        ]

    def get_id(self, obj):

        return obj.album_uri

    def get_is_liked(self, obj):
        return False

    def get_total_likes(self, obj):
        return 0


class ArtistSerializer(serializers.ModelSerializer):
    # name = serializers.CharField(max_length=255, min_length=3, read_only=True)
    # album_id = serializers.CharField()
    # artists = ArtistsSerializer
    # tracks = TrackSerializer(many=True)
    images = ArtistImagesSerializer(many=True)
    # tracks = TrackSerializer()
    # posts = PostsSerializer()
    albums = AlbumsSerializer(many=True)
    id = serializers.SerializerMethodField()

    class Meta:
        model = Artist
        fields = [
            'id',
            # 'uuid',
            'name',
            'artist_uri',
            'images',
            # 'album_id',

            'albums',
            # 'images',
            # 'created_at',
            # 'updated_at',
            # 'likes_count',
        ]

    def get_id(self, obj):

        return obj.artist_uri

class ArtistListSerializer(serializers.ModelSerializer):
    # name = serializers.CharField(max_length=255, min_length=3, read_only=True)
    # album_id = serializers.CharField()
    # artists = ArtistsSerializer
    # tracks = TrackSerializer(many=True)
    # tracks = TrackSerializer()
    # posts = PostsSerializer()
    images = ArtistImagesSerializer(many=True)
    # albums = AlbumsSerializer(many=True)
    id = serializers.SerializerMethodField()

    class Meta:
        model = Artist
        fields = [
            'id',
            # 'uuid',
            'name',
            'artist_uri',
            # 'album_id',
            # 'artists',
            # 'albums',
            'images',
            # 'created_at',
            # 'updated_at',
            # 'likes_count',
        ]

    def get_id(self, obj):

        return obj.artist_uri
