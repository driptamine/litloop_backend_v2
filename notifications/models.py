from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from users.models import User

# Create your models here.

class Notification(models.Model):
    from_user           = models.ForeignKey(User, on_delete=models.CASCADE, related_name='from_user_noti')
    to_user             = models.ForeignKey(User, on_delete=models.CASCADE, related_name='to_user_noti')
    date                = models.DateTimeField(auto_now_add=True, null=True)
    is_read             = models.BooleanField(default=False)
    target_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='notify_target', blank=True, null=True)
    target_object_id    = models.PositiveIntegerField(null=True)
    target              = GenericForeignKey('target_content_type', 'target_object_id')
