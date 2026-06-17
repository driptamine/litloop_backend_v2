import os
import m3u8

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

def validate_mp4_extension(value):
    ext = os.path.splitext(value.name)[1]  # Get the file extension
    if ext.lower() != '.mp4':
        raise ValidationError("Only .mp4 files are allowed.")


class Video(models.Model):
    PENDING = 'Pending'
    PROCESSING = 'Processing'
    COMPLETED = 'Completed'

    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (PROCESSING, 'Processing'),
        (COMPLETED, 'Completed'),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    name = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500, blank=True)
    description = models.TextField()

    video_file = models.FileField(upload_to="videos",validators=[validate_mp4_extension])
    thumbnail = models.FileField(upload_to="thumbnails",null=True,blank=True)
    duration = models.CharField(max_length=20, blank=True,null=True)
    hls_file = models.CharField(max_length=500,blank=True,null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    is_running = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


    def url_from_path(filename):
        # TODO: find a way to preserver http - https ...
        return "{0}{1}".format(settings.MEDIA_URL, filename.replace(settings.MEDIA_ROOT, ""))

    @property
    def hls_info(self):
        """Property used on serializers
        Returns hls info, curated to be read by video.js
        """

        res = {}
        if self.hls_file:
            if os.path.exists(self.hls_file):
                hls_file = self.hls_file
                p = os.path.dirname(hls_file)
                m3u8_obj = m3u8.load(hls_file)
                if os.path.exists(hls_file):
                    res["master_file"] = url_from_path(hls_file)
                    for iframe_playlist in m3u8_obj.iframe_playlists:
                        uri = os.path.join(p, iframe_playlist.uri)
                        if os.path.exists(uri):
                            resolution = iframe_playlist.iframe_stream_info.resolution[1]
                            res["{}_iframe".format(resolution)] = url_from_path(uri)
                    for playlist in m3u8_obj.playlists:
                        uri = os.path.join(p, playlist.uri)
                        if os.path.exists(uri):
                            resolution = playlist.stream_info.resolution[1]
                            res["{}_playlist".format(resolution)] = url_from_path(uri)
        return res
