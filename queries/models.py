from django.db import models

# Create your models here.
class Query(models.Model):
    query_text = models.CharField(max_length=255, blank=True, null=True)
    suggestion = models.CharField(max_length=255, blank=True, null=True)

# class Query(models.Model):
#     query_text = models.CharField(max_length=255, blank=True, null=True)
#     suggestion = models.CharField(max_length=255, blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         unique_together = ('query_text', 'suggestion')


class UserQuery(models.Model):
    query_text = models.CharField(max_length=255, blank=True, null=True)
    suggestion = models.CharField(max_length=255, blank=True, null=True)


class BraveQuery(models.Model):
    query_text = models.CharField(max_length=255, blank=True, null=True)
    suggestion = models.CharField(max_length=255, blank=True, null=True)

class GoogleQuery(models.Model):
    query_text = models.CharField(max_length=255, blank=True, null=True)
    suggestion = models.CharField(max_length=255, blank=True, null=True)

class BingQuery(models.Model):
    query_text = models.CharField(max_length=255, blank=True, null=True)
    suggestion = models.CharField(max_length=255, blank=True, null=True)
