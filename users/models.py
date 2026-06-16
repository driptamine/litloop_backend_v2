import json
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from rest_framework_simplejwt.tokens import RefreshToken


from users.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    username    = models.CharField(max_length=255, unique=True, db_index=True, blank=True, null=True)
    email       = models.EmailField(max_length=255, unique=True, db_index=True)
    avatar      = models.CharField(max_length=500, blank=True, null=True)

    is_verified = models.BooleanField(default=False)
    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)


    # following = models.ManyToManyField("self", blank=True)
    # followers = models.ManyToManyField("self", blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    def access_token(self):
        refresh_token = RefreshToken.for_user(self)

        return str(refresh_token.access_token)

    def refresh_token(self):
        refresh_token = RefreshToken.for_user(self)

        return str(refresh_token)

    @property
    def thumbnail_url(self):
        return self.avatar

    @property
    def name(self):
        return self.username

    @property
    def logo(self):
        return self.avatar
