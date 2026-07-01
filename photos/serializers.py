from rest_framework import serializers
from photos.models import Photo
from litloop_project.r2_storage import r2_url

class PhotoSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    gcs_url = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = [
            'id',
            'url',
            'gcs_url',
            'gcs_key',
            'title',
            'friendly_token',
            'likes',
            'dislikes',
            'views',
            'impressions',
        ]

    def get_url(self, obj):
        return r2_url(obj.gcs_key) or r2_url(obj.s3_key)

    def get_gcs_url(self, obj):
        return r2_url(obj.gcs_key)
