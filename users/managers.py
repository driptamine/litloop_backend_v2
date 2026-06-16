# https://chatgpt.com/c/681f1947-13f8-800c-a93c-9cd62aeeff58
# your_app/models/managers.py

from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):

    def create_user(self, email, username=None, password=None, **extra_fields):
        if not email:
            raise TypeError('Users must have an email address')
        
        user = self.model(
            email = self.normalize_email(email),
            username = username,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(
            username=username,
            email=email,
            password=password,
            **extra_fields
        )
