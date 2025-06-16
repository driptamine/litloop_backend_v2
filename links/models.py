from django.db import models


class Hashtag(models.Model):
    name = models.CharField(max_length=100, unique=True)


class Link(models.Model):
    user       = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    title      = models.CharField(max_length=255, null=True, blank=True)   # add this
    url        = models.URLField()
    hashtags   = models.ManyToManyField('links.Hashtag', through='LinkTag', related_name='links')
    status     = models.CharField(max_length=20, default='unread')  # add this (optional)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    time_added = models.DateTimeField(null=True, blank=True)  # optional, for CSV timestamps


class LinkTag(models.Model):
    link     = models.ForeignKey('links.Link', on_delete=models.CASCADE)
    hashtag  = models.ForeignKey('links.Hashtag', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)  # extra info example

    class Meta:
        unique_together = ('link', 'hashtag')
