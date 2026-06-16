from django.apps import apps
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.html import strip_tags

from artists.models import Artist
from tracks.models import Track
from images.models import Image
from albums.models import Album
from users.models import User
from posts import helpers

class Playlist(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=400, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    friendly_token = models.CharField(max_length=100, blank=True, null=True)
    
    user = models.ForeignKey(User, related_name='playlists', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title if self.title else f"Playlist {self.id}"

    def get_absolute_url(self, api=False):
        if api:
            # return reverse("api_get_playlist", kwargs={"friendly_token": self.friendly_token})
            return f"/api/playlists/{self.friendly_token}/"
        else:
            # return reverse("get_playlist", kwargs={"friendly_token": self.friendly_token})
            return f"/playlists/{self.friendly_token}/"

    @property
    def url(self):
        return self.get_absolute_url()

    @property
    def api_url(self):
        return self.get_absolute_url(api=True)

    def save(self, *args, **kwargs):
        strip_text_items = ["title", "description"]
        for item in strip_text_items:
            val = getattr(self, item, None)
            if val:
                setattr(self, item, strip_tags(str(val)))
        
        if self.title:
            self.title = self.title[:99]

        if not self.friendly_token:
            while True:
                friendly_token = helpers.produce_friendly_token()
                if not Playlist.objects.filter(friendly_token=friendly_token).exists():
                    self.friendly_token = friendly_token
                    break
        super(Playlist, self).save(*args, **kwargs)
