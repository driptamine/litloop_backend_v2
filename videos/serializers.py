from rest_framework import serializers
from videos.models import Video
from litloop_project.r2_storage import r2_url

class VideoSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    gcs_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            'id',
            'url',
            'gcs_url',
            'gcs_key',
            'thumbnail_url',
            'title',
            'description',
            'likes',
            'dislikes',
            'views',
            'impressions',
        ]

    def get_url(self, obj):
        return r2_url(obj.gcs_key) or r2_url(obj.s3_key)

    def get_gcs_url(self, obj):
        return r2_url(obj.gcs_key)

    def get_thumbnail_url(self, obj):
        return r2_url(obj.thumbnail)
