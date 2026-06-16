from django.conf import settings
from rest_framework import serializers
from videos.models import Video

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
        if obj.s3_key:
            return f"https://dgsmmq1mgfewt.cloudfront.net/{obj.s3_key}"
        return None

    def get_gcs_url(self, obj):
        if obj.gcs_key:
            return f"https://storage.googleapis.com/{settings.GCS_BUCKET_NAME}/{obj.gcs_key}"
        return None

    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            return f"https://dgsmmq1mgfewt.cloudfront.net/{obj.thumbnail}"
        return None
