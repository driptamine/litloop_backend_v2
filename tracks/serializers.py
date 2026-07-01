from django.apps import apps
from django.contrib import auth
from rest_framework import serializers
from litloop_project.r2_storage import r2_url
from rest_framework.exceptions import AuthenticationFailed
from users.serializers import UserSerializer

# import tracks.models as Track

# from artists.models import Artist
# from albums.models import Album
# from .models import Track



Track = apps.get_model(app_label='tracks', model_name='Track')
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
        ref_name = "TrackArtist"

    def get_id(self, obj):

        return obj.artist_uri


class TracksSerializer(serializers.ModelSerializer):

    artists = ArtistsSerializer(many=True)
    user = UserSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()
    total_likes = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    class Meta:
        model = Track
        fields = [
            'id',
            'pk',
            'name',
            'track_uri',
            'user',
            'is_liked',
            'total_likes',
            'artists',
            'track_number',

        ]

    def get_id(self, obj):

        return obj.track_uri

    def get_is_liked(self, obj):
        return False

    def get_total_likes(self, obj):
        return 0


class ImagesSerializer(serializers.ModelSerializer):

    # artists = ArtistsSerializer(many=True)

    class Meta:
        model = Image
        fields = [
            'id',
            'url',
            'height',
            'width',

        ]


class AlbumSerializer(serializers.ModelSerializer):

    artists = ArtistsSerializer(many=True)
    tracks = TracksSerializer(many=True)
    images = ImagesSerializer(many=True)
    id = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = [
            'id',
            'name',
            'album_uri',
            'artists',
            'tracks',
            'images',
        ]

    def get_id(self, obj):

        return obj.album_uri

class TrackSerializer(serializers.ModelSerializer):
    artists = ArtistsSerializer(many=True)
    album = AlbumSerializer()
    user = UserSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()
    total_likes = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    gcs_url = serializers.SerializerMethodField()

    class Meta:
        model = Track
        fields = [
            'id',
            'pk',
            # 'uuid',
            'name',
            'user',
            's3_key',
            'gcs_url',
            'gcs_key',
            'track_uri',
            'track_number',
            'is_liked',
            'total_likes',
            'artists',
            'album',
            'created_at',
            'updated_at',
            'release_date',
        ]


    def get_id(self, obj):

        return obj.track_uri

    def get_is_liked(self, obj):
        return False

    def get_total_likes(self, obj):
        return 0

    def get_gcs_url(self, obj):
        return r2_url(obj.gcs_key)


class AlbumSerializer(serializers.ModelSerializer):

    artists = ArtistsSerializer(many=True)
    # tracks = TracksSerializer(many=True)
    images = ImagesSerializer(many=True)
    id = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = [
            'id',
            'name',
            'album_uri',
            'artists',
            # 'tracks',
            'images',
        ]

    def get_id(self, obj):

        return obj.album_uri


class TrackListSerializer(serializers.ModelSerializer):
    artists = ArtistsSerializer(many=True)
    album = AlbumSerializer()
    user = UserSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()
    total_likes = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    gcs_url = serializers.SerializerMethodField()

    class Meta:
        model = Track
        fields = [
            'id',
            'pk',
            # 'uuid',
            'name',
            'user',
            's3_key',
            'gcs_url',
            'gcs_key',
            'track_uri',
            'track_number',
            'is_liked',
            'total_likes',
            'artists',
            'album',
            'created_at',
            'updated_at',
            'release_date',
        ]


    def get_id(self, obj):

        return obj.track_uri

    def get_is_liked(self, obj):
        return False

    def get_total_likes(self, obj):
        return 0

    def get_gcs_url(self, obj):
        return r2_url(obj.gcs_key)
