from django.db import models
from users.models import User
from videos.models import Video
from photos.models import Photo
from tracks.models import Track


class Chat(models.Model):
    name        = models.SlugField(max_length=20, blank=True, null=True)
    image_url   = models.CharField(max_length=400, blank=True, null=True)
    description = models.CharField(max_length=400, blank=True, null=True)
    participants = models.ManyToManyField(User, related_name="chats", blank=True)


class Message(models.Model):
    chat         = models.ForeignKey(Chat, on_delete=models.SET_NULL, null=True, blank=True, related_name="messages")
    user         = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    text         = models.TextField(blank=True)
    videos       = models.ManyToManyField(Video, through='MessageVideo', related_name='video_messages', blank=True)
    photos       = models.ManyToManyField(Photo, through='MessagePhoto', related_name='photo_messages', blank=True)
    tracks       = models.ManyToManyField(Track, through='MessageTrack', related_name='track_messages', blank=True)
    voice_messages = models.ManyToManyField('VoiceMessage', through='MessageVoice', related_name='voice_messages', blank=True)
    attachments  = models.JSONField(default=list, blank=True)
    is_read      = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)


class MessageVideo(models.Model):
    message = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True, blank=True)
    video   = models.ForeignKey(Video, on_delete=models.SET_NULL, null=True, blank=True)


class MessagePhoto(models.Model):
    message = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True, blank=True)
    photo   = models.ForeignKey(Photo, on_delete=models.SET_NULL, null=True, blank=True)


class MessageTrack(models.Model):
    message = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True, blank=True)
    track   = models.ForeignKey(Track, on_delete=models.SET_NULL, null=True, blank=True)


class MessageVoice(models.Model):
    message = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True, blank=True)
    voice_message = models.ForeignKey('VoiceMessage', on_delete=models.SET_NULL, null=True, blank=True)


class VoiceMessage(models.Model):
    s3_key       = models.CharField(max_length=400, null=True, blank=True)
    gcs_key      = models.CharField(max_length=400, null=True, blank=True)
    filename     = models.CharField(max_length=400, null=True, blank=True)
    duration     = models.FloatField(default=0.0) # seconds
    user         = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    @property
    def url(self):
        from django.conf import settings
        if self.gcs_key:
            if self.gcs_key.startswith('http'):
                return self.gcs_key
            return f"https://storage.googleapis.com/{settings.GCS_BUCKET_NAME}/{self.gcs_key}"
        if self.s3_key:
            if self.s3_key.startswith('http'):
                return self.s3_key
            return f"https://{settings.AWS_STORAGE_BUCKET_NAME_DRIPTAMINE}.s3.amazonaws.com/{self.s3_key}"
        return None


class Call(models.Model):
    CALL_TYPES = [
        ('voice', 'Voice'),
        ('video', 'Video'),
    ]
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('missed', 'Missed'),
        ('rejected', 'Rejected'),
    ]

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="calls")
    caller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="calls_initiated")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="calls_received", null=True, blank=True)
    
    call_type = models.CharField(max_length=10, choices=CALL_TYPES, default='voice')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    @property
    def duration(self):
        if self.started_at and self.ended_at:
            return (self.ended_at - self.started_at).total_seconds()
        return 0


# class Invite(models.Model):
#     pass
