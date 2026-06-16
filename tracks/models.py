from django.apps import apps
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from tracks.managers import TrackManager


class SpotifyTrack(models.Model):
    s3_key       = models.CharField(max_length=400, null=True, blank=True)
    gcs_key      = models.CharField(max_length=400, null=True, blank=True)
    filename     = models.CharField(max_length=400)

class Track(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('attached', 'Attached'),
    ]

    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    s3_key       = models.CharField(max_length=400, null=True, blank=True)
    gcs_key      = models.CharField(max_length=400, null=True, blank=True)
    filename     = models.CharField(max_length=400, null=True, blank=True)

    track_uri    = models.CharField(max_length=400)
    name         = models.CharField(max_length=400)
    track_number = models.CharField(max_length=400, default="")
    artists      = models.ManyToManyField('artists.Artist', related_name='tracks', blank=True)

    album        = models.ForeignKey('albums.Album', related_name='tracks', on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    release_date = models.DateTimeField(null=True, blank=True)

    user         = models.ForeignKey('users.User', related_name='tracks', on_delete=models.CASCADE, null=True, blank=True)

    likes        = models.ManyToManyField('users.User', through='TrackLike', blank=True, related_name='track_likes')
    plays        = models.ManyToManyField('users.User', through='TrackPlay', blank=True, related_name='track_plays')


    # tags     = ManyToManyField('users.User', through=TrackLikeTag, related_query_name='track_liketags', null=True)
    # comments = ManyToManyField('users.User', through=TrackComment, related_query_name='track_comments', null=True)

    # author         = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    # deezer_id      = models.CharField(max_length=MAX_LENGTH, null=True, unique=True)
    # spotify_id     = models.CharField(max_length=MAX_LENGTH, null=True, unique=True)
    # apple_music_id = models.CharField(max_length=MAX_LENGTH, null=True, unique=True)
    # isrc           = models.CharField(max_length=MAX_LENGTH, null=True)

    # objects = TrackManager()


class TrackLike(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    liked_by = models.ForeignKey('users.User', on_delete=models.CASCADE)

class TrackDislike(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    dislike_by = models.ForeignKey('users.User', on_delete=models.CASCADE)

class TrackImpression(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    user  = models.ForeignKey('users.User', on_delete=models.CASCADE)

class TrackView(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    user  = models.ForeignKey('users.User', on_delete=models.CASCADE)

class TrackPlay(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    user  = models.ForeignKey('users.User', on_delete=models.CASCADE)


# import artists.models as Artist
# import albums.models as Album
# import likes.models as Like


# Track = apps.get_model(app_label='tracks', model_name='Track')
# Artist = apps.get_model(app_label='artists', model_name='Artist')
# Album = apps.get_model(app_label='albums', model_name='Album')
# Like = apps.get_model(app_label='likes', model_name='Like')

# class UserUploadedTrack(models.Model):
#     name = models.CharField()
#     artist_name = models.CharField()
#     user = models.ForeignKey('users.User', related_name='tracks')
#     state = models.CharField(max_length=20, choices=MEDIA_STATES, default=helpers.get_portal_workflow(), db_index=True)
