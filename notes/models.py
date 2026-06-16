from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

class Page(MPTTModel):
    title = models.CharField(max_length=200)
    parent = TreeForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children',
        on_delete=models.CASCADE
    )
    is_locked = models.BooleanField(default=False)
    is_private = models.BooleanField(default=True)
    # author = models.ForeignKey('users.User', related_name='pages', on_delete=models.SET_NULL, null=True, blank=True)

    class MPTTMeta:
        order_insertion_by = ['title']

class Block(models.Model):
    page = models.ForeignKey(Page, related_name='blocks', on_delete=models.CASCADE)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
