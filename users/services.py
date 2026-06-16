from typing import Tuple

from django.db import transaction
from django.core.management.utils import get_random_secret_key
from django.utils import timezone

from django.utils.crypto import get_random_string

from users.models import User




def get_now():
    return timezone.now()

def user_create(email, password=None, **extra_fields) -> User:
    extra_fields = {
        'is_staff': False,
        'is_superuser': False,
        **extra_fields
    }

    user = User(email=email, **extra_fields)

    if password:
        user.set_password(password)
    else:
        user.set_unusable_password()

    user.full_clean()
    user.save()

    return user


def user_create_superuser(email, password=None, **extra_fields):
    extra_fields = {
        **extra_fields,
        'is_staff': True,
        'is_superuser': True
    }

    user = user_create(email=email, password=password, **extra_fields)

    return user


def user_record_login(*, user):
    user.last_login = get_now()
    user.save()

    return user


@transaction.atomic
def user_change_secret_key(*, user):
    user.secret_key = get_random_secret_key()
    user.full_clean()
    user.save()

    return user


@transaction.atomic
def user_get_or_create(*, email, **extra_data):
    user = User.objects.filter(email=email).first()

    if user:
        return user, False

    username = extra_data.get('username')
    if username:
        # Check if username exists for a different user
        if User.objects.filter(username=username).exclude(email=email).exists():
            extra_data['username'] = f"{username}_{get_random_string(5)}"

    return user_create(email=email, **extra_data), True

# 
# def user_update():
#
