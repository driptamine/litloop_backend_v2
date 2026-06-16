import tempfile

from django.db import models
from django.db.models.signals import m2m_changed, post_delete, post_save, pre_delete
from django.dispatch import receiver
from django.utils.html import strip_tags

from users.models import User
from photos.models import Photo
from videos.models import Video
from tracks.models import Track
from playlists.models import Playlist

from posts import helpers


class Post(models.Model):
    videos      = models.ManyToManyField(Video,    through="PostVideo",    blank=True,    related_name="postvideos")
    tracks      = models.ManyToManyField(Track,    through="PostTrack",    blank=True,    related_name="posttracks")
    photos      = models.ManyToManyField(Photo,    through="PostPhoto",    blank=True,    related_name="postphotos")
    playlists   = models.ManyToManyField(Playlist, through="PostPlaylist", blank=True,    related_name="postplaylists")

    title       = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True)
    friendly_id = models.CharField(max_length=100, blank=True)

    author      = models.ForeignKey(
        User,
        related_name='posts',
        # on_delete=models.CASCADE
        on_delete=models.SET_NULL, null=True, blank=True
    )


    likes_count       = models.IntegerField(default=0)
    dislikes_count    = models.IntegerField(default=0)
    views_count       = models.IntegerField(default=0)
    impressions_count = models.IntegerField(default=0)

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']


    def save(self, *args, **kwargs):
        strip_text_items = ["title", "description"]
        for item in strip_text_items:
            val = getattr(self, item, "")
            if val:
                setattr(self, item, strip_tags(str(val)))
        
        if self.title:
            self.title = self.title[:99]

        if not self.friendly_id:
            while True:
                friendly_id = helpers.produce_friendly_token()
                if not Post.objects.filter(friendly_id=friendly_id):
                    self.friendly_id = friendly_id
                    break
        super(Post, self).save(*args, **kwargs)


# ======== POST STATS ======= #
class PostLike(models.Model):
    post        = models.ForeignKey(Post, on_delete=models.CASCADE)
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    liked_at    = models.DateTimeField(auto_now_add=True)

class PostDislike(models.Model):
    post        = models.ForeignKey(Post, on_delete=models.CASCADE)
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    disliked_at = models.DateTimeField(auto_now_add=True)

class PostImpression(models.Model):
    post        = models.ForeignKey(Post, on_delete=models.CASCADE)
    user        = models.ForeignKey(User, on_delete=models.CASCADE)

class PostView(models.Model):
    post        = models.ForeignKey(Post, on_delete=models.CASCADE)
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    viewed_at   = models.DateTimeField(auto_now_add=True)


# ========= POST Attachments ========= #
class PostPhoto(models.Model):
    post        = models.ForeignKey(Post, on_delete=models.CASCADE)
    photo       = models.ForeignKey('photos.Photo', on_delete=models.CASCADE)
    order       = models.IntegerField(default=1)

class PostVideo(models.Model):
    post        = models.ForeignKey(Post, on_delete=models.CASCADE)
    video       = models.ForeignKey('videos.Video', on_delete=models.CASCADE)
    order       = models.IntegerField(default=1)

class PostTrack(models.Model):
    post        = models.ForeignKey(Post, on_delete=models.CASCADE)
    track       = models.ForeignKey('tracks.Track', on_delete=models.CASCADE)
    order       = models.IntegerField(default=1)

class PostPlaylist(models.Model):
    post        = models.ForeignKey(Post, on_delete=models.CASCADE)
    playlist    = models.ForeignKey('playlists.Playlist', on_delete=models.CASCADE)
    order       = models.IntegerField(default=1)
