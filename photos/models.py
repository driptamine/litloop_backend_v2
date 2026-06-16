import uuid

from django.db import models
from django.utils.html import strip_tags

from posts import helpers
from posts.helpers import original_media_file_path, original_thumbnail_file_path
from users.models import User

class Photo(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('attached', 'Attached'),
    ]

    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    s3_key          = models.CharField(max_length=400, null=True)
    gcs_key         = models.CharField(max_length=400, null=True, blank=True)
    filename        = models.CharField(max_length=400, null=True)

    user            = models.ForeignKey("users.User", on_delete=models.CASCADE, null=True, blank=True)
    title           = models.TextField(blank=True, null=True)


    user_featured   = models.BooleanField(default=False)
    friendly_token  = models.CharField(blank=True, max_length=12, db_index=True)

    likes        = models.IntegerField(default=0)
    dislikes     = models.IntegerField(default=0)
    views        = models.IntegerField(default=0)
    impressions  = models.IntegerField(default=0)


class PhotoLike(models.Model):
    photo    = models.ForeignKey(Photo, on_delete=models.CASCADE)
    liked_by = models.ForeignKey('users.User', on_delete=models.CASCADE)

class PhotoDislike(models.Model):
    photo      = models.ForeignKey(Photo, on_delete=models.CASCADE)
    dislike_by = models.ForeignKey('users.User', on_delete=models.CASCADE)

class PhotoImpression(models.Model):
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE)
    user  = models.ForeignKey('users.User', on_delete=models.CASCADE)

class PhotoView(models.Model):
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE)
    user  = models.ForeignKey('users.User', on_delete=models.CASCADE)


class PhotoAlbum(models.Model):
    add_date       = models.DateTimeField(auto_now_add=True, db_index=True)
    description    = models.TextField(blank=True, help_text="description")
    friendly_token = models.CharField(blank=True, max_length=12, db_index=True)
    photo          = models.ManyToManyField(Photo, through="PhotoAlbumItem", blank=True)
    title          = models.CharField(max_length=100, db_index=True)

    user           = models.ForeignKey("users.User", on_delete=models.CASCADE, db_index=True, related_name="photoalbums")

    def __str__(self):
        return self.title


    def set_ordering(self, photo, ordering):
        if photo not in self.photo.all():
            return False
        pa = PhotoAlbumItem.objects.filter(photo_album=self, photo=photo).first()
        if pa and isinstance(ordering, int) and 0 < ordering:
            pa.ordering = ordering
            pa.save()
            return True
        return False

    def add_photo(self, photo):
        """Adds a photo to the album and returns the created PhotoAlbumItem or None if already exists."""
        if PhotoAlbumItem.objects.filter(photo_album=self, photo=photo).exists():
            return None

        # Determine next ordering
        last_item = self.photoalbumitem_set.order_by('-ordering').first()
        next_ordering = (last_item.ordering + 1) if last_item else 1

        return PhotoAlbumItem.objects.create(
            photo_album=self,
            photo=photo,
            ordering=next_ordering
        )

    def save(self, *args, **kwargs):
        strip_text_items = ["title", "description"]
        for item in strip_text_items:
            setattr(self, item, strip_tags(getattr(self, item, None)))
        self.title = self.title[:99]

        if not self.friendly_token:
            while True:
                friendly_token = helpers.produce_friendly_token()
                if not PhotoAlbum.objects.filter(friendly_token=friendly_token):
                    self.friendly_token = friendly_token
                    break
        super(PhotoAlbum, self).save(*args, **kwargs)

    @property
    def thumbnail_url(self):
        pai = self.photoalbumitem_set.first()
        if pai and pai.photo.thumbnail:
            return helpers.url_from_path(pai.photo.thumbnail.path)
        return None


class PhotoAlbumItem(models.Model):
    """Helper model to store playlist specific media"""

    action_date = models.DateTimeField(auto_now=True)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE)
    photo_album = models.ForeignKey(PhotoAlbum, on_delete=models.CASCADE)
    ordering = models.IntegerField(default=1)

    class Meta:
        ordering = ["ordering", "-action_date"]
