from django.db import models


class Website(models.Model):
    url        = models.URLField(unique=True, blank=True, null=True)
    title      = models.TextField(blank=True, null=True)
    body       = models.TextField(blank=True, null=True)
    favicon    = models.CharField(max_length=400, blank=True, null=True)
    query      = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class WebsiteImage(models.Model):
    url         = models.URLField(blank=True, null=True)
    title       = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    page_url    = models.URLField(blank=True, null=True)
    thumbnail   = models.URLField(blank=True, null=True)
    height      = models.CharField(max_length=400, blank=True, null=True)
    width       = models.CharField(max_length=400, blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
