# -*- coding: utf-8 -*-
import os
import shutil

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.files import File
from django.http import JsonResponse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from users.auth_utils import jwt_required

# from litloop_project.permissions import user_allowed_to_upload
# from media.helpers import rm_file
# from media.models import Media

# from media.helpers import rm_file
from videos.models import Video
