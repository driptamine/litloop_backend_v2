from django.db import models
from posts.helpers import original_media_file_path, original_thumbnail_file_path
from users.models import User

class Video(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('attached', 'Attached'),
    ]
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    visibility  = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')

    s3_key      = models.CharField(max_length=400, null=True, blank=True)
    gcs_key     = models.CharField(max_length=400, null=True, blank=True)
    filename    = models.CharField(max_length=400, null=True, blank=True)
    hls_s3      = models.CharField(max_length=400, null=True, blank=True)

    title       = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)

    video_file  = models.CharField(max_length=400, null=True, blank=True)

    sprites     = models.CharField(max_length=400, null=True, blank=True)
    thumbnail   = models.CharField(max_length=400, null=True, blank=True)

    likes       = models.IntegerField(default=0)
    dislikes    = models.IntegerField(default=0)
    views       = models.IntegerField(default=0)
    impressions = models.IntegerField(default=0)

    # song = models.ForeignKey(Song, on_delete=models.CASCADE, blank=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True)


class VideoWatchProgress(models.Model):
    user          = models.ForeignKey(User, on_delete=models.CASCADE)
    video         = models.ForeignKey(Video, on_delete=models.CASCADE)
    playback_time = models.FloatField(default=0.0)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'video')


class VideoPlaylist(models.Model):
    title  = models.CharField(max_length=900, null=True, blank=True)
    videos = models.ManyToManyField(Video, through='VideoPlaylistItem')

class VideoPlaylistItem(models.Model):

    video    = models.ForeignKey(Video, on_delete=models.CASCADE)
    playlist = models.ForeignKey(VideoPlaylist, on_delete=models.CASCADE)
    ordering = models.IntegerField(default=1)
