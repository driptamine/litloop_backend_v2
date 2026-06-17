# reference: https://github.com/Fedor-Skorokhodov/Blog_Django/blob/21fe83f46de9662913736002313b969da3497e11/post/models.py

from django.db import models
from home.models import UserModel


class Post(models.Model):
    friendly_token = models.CharField(blank=True, max_length=12, db_index=True)
    author = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    videos = models.ManyToManyField(Video, through="PostVideo")
    tracks = models.ManyToManyField(Track, through="PostTrack")
    photos = models.ManyToManyField(Photo, through="PostPhoto")
    playlists = models.ManyToManyField(Playlist, through="PostPlaylist")


    def save(self, *args, **kwargs):
        strip_text_items = ["title", "description"]
        for item in strip_text_items:
            setattr(self, item, strip_tags(getattr(self, item, None)))
        self.title = self.title[:99]

        if not self.friendly_token:
            while True:
                friendly_token = helpers.produce_friendly_token()
                if not Post.objects.filter(friendly_token=friendly_token):
                    self.friendly_token = friendly_token
                    break
        super(Post, self).save(*args, **kwargs)


class Photo(models.Model):
    image_file = models.FileField(upload_to='post/images')
    title = models.TextField(blank=True,null=True)
    description = models.TextField(blank=True,null=True)

class PostPhoto(models.Model):
    post = models.ForeignKey(Post)
    photo = models.ForeignKey(Photo)
    order = models.IntegerField(default=1)

class Video(models.Model):
    video_file = models.FileField(upload_to='post/videos')
    title = models.TextField(blank=True,null=True)
    description = models.TextField(blank=True,null=True)

class PostVideo(models.Model):
    post = models.ForeignKey(Post)
    video = models.ForeignKey(Video)
    order = models.IntegerField(default=1)

class Track(models.Model):
    artists = models.ManyToManyField(Artist, through="TrackArtist")
    track_file = models.FileField(upload_to='post/tracks')
    title = models.TextField(blank=True,null=True)

class PostTrack(models.Model):
    post = models.ForeignKey(Post)
    track = models.ForeignKey(Track)
    order = models.IntegerField(default=1)


class Comment(models.Model):
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    author = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    answer_to = models.ForeignKey('self', null=True, default=None, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.FileField(upload_to='comments/images', null=True, default=None)
    video = models.FileField(upload_to='comments/videos', null=True, default=None)
    track = models.FileField(upload_to='comments/tracks', null=True, default=None)
