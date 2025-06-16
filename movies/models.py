from django.db import models
from users.models import User

# Create your models here.
class Movie(models.Model):
    tmdb_id     = models.IntegerField(null=True, blank=True)
    imdb_id     = models.IntegerField(null=True, blank=True)
    title       = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    movie_file  = models.TextField(null=True, blank=True)
    poster      = models.TextField(null=True, blank=True)

    likes_count       = models.IntegerField(default=0)
    dislikes_count    = models.IntegerField(default=0)
    views_count       = models.IntegerField(default=0)
    impressions_count = models.IntegerField(default=0)


class ImdbMovie(models.Model):
    imdb_id         = models.CharField(max_length=20, unique=True)  # "Const"
    title           = models.CharField(max_length=255)
    original_title  = models.CharField(max_length=255, blank=True)
    url             = models.URLField(blank=True)
    title_type      = models.CharField(max_length=50, blank=True)

    imdb_rating     = models.FloatField(null=True, blank=True)
    user_rating     = models.FloatField(null=True, blank=True)  # "Your Rating"

    runtime_minutes = models.PositiveIntegerField(null=True, blank=True)
    year            = models.PositiveIntegerField(null=True, blank=True)
    release_date    = models.DateField(null=True, blank=True)

    genres          = models.CharField(max_length=255, blank=True)  # optional: split later
    num_votes       = models.PositiveIntegerField(null=True, blank=True)

    directors       = models.CharField(max_length=255, blank=True)
    description     = models.TextField(blank=True)

    created_at      = models.DateField(null=True, blank=True)  # CSV: "Created"
    modified_at     = models.DateField(null=True, blank=True)  # CSV: "Modified"
    date_rated      = models.DateField(null=True, blank=True)

    position        = models.PositiveIntegerField(null=True, blank=True)  # Optional

    def __str__(self):
        return self.title or self.imdb_id


class WatchlistItem(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist_items')
    movie      = models.ForeignKey(ImdbMovie, on_delete=models.CASCADE, related_name='watchlisted_by')

    user_rating  = models.FloatField(null=True, blank=True)
    date_added   = models.DateField(auto_now_add=True)
    date_rated   = models.DateField(null=True, blank=True)
    watched      = models.BooleanField(default=False)
    notes        = models.TextField(blank=True)

    class Meta:
        unique_together = ('user', 'movie')  # Prevent duplicates
        ordering = ['-date_added']

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"



class MovieImpression(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)

class MovieView(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
