# reference: https://github.com/Fedor-Skorokhodov/Blog_Django/blob/21fe83f46de9662913736002313b969da3497e11/post/models.py

from django.db import models
from home.models import UserModel


class BlogPost (models.Model):
    name = models.CharField(max_length=50)
    content = models.TextField()
    date = models.DateTimeField(auto_now=False, auto_now_add=True)


class Photo(models.Model):
    image = models.FileField(upload_to='post/images')
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)


class BlogVideo (models.Model):
    video = models.FileField(upload_to='post/videos')
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)


class BlogAudio (models.Model):
    audio = models.FileField(upload_to='post/audio')
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)


class Comment (models.Model):
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    author = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    answer_to = models.ForeignKey('self', null=True, default=None, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.FileField(upload_to='comments/images', null=True, default=None)
    video = models.FileField(upload_to='comments/videos', null=True, default=None)
    track = models.FileField(upload_to='comments/tracks', null=True, default=None)
