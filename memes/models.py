from django.db import models
from users.models import User


class Meme(models.Model):
    meme_id    = models.CharField(max_length=500, unique=True)
    title      = models.TextField()
    url        = models.TextField()
    post_link  = models.TextField()
    subreddit  = models.CharField(max_length=255)
    author     = models.CharField(max_length=255)
    nsfw       = models.BooleanField(default=False)
    spoiler    = models.BooleanField(default=False)
    ups        = models.IntegerField(default=0)
    preview    = models.TextField(blank=True, null=True)

    liked_by   = models.ManyToManyField(User, blank=True, related_name='liked_memes')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title[:80]
