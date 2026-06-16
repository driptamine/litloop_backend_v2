# -*- coding: utf-8 -*-
# from django.conf.urls import re_path
from django.urls import path
from . import views

# from hitman_rest_api.channels import TaskProgressConsumer
from uploader.channels import TaskProgressConsumer
from uploader.websocket.websocket_views_no_drf import (
    get_hitmen_view, start_new_hit_job_view, schedule_new_hit_job_view, create_user_view
)

from .views_no_drf import presigned_url_api
from . import gcs_multipart_views_no_drf as gcs_multipart_views

app_name = "uploader"

urlpatterns = [
    path('presigned-url/', presigned_url_api, name='presigned_url'),

    # GCS Multipart Upload (Matches S3 Flow)
    path('gcs/create_presigned_url/', gcs_multipart_views.gcs_initiate_multipart_upload, name='gcs_initiate'),
    path('gcs/get_presigned_url/', gcs_multipart_views.gcs_get_part_presigned_url, name='gcs_get_part'),
    path('gcs/complete_upload/', gcs_multipart_views.gcs_complete_multipart_upload, name='gcs_complete'),

    # Hitmen / Jobs
    path('hitmen/all/', get_hitmen_view, name='hitmen-all'),
    path('hitmen/start-job/', start_new_hit_job_view, name='start-job'),
    path('hitmen/schedule/', schedule_new_hit_job_view, name='schedule-job'),
    path('hitmen/create-user/', create_user_view, name='create-user'),
]

# ref docker-celery
websocket_urlpatterns = [
    # path("task/upload/<str:taskID>/", TaskProgressConsumer.as_asgi()),
    # path("task/transcoding/<str:taskID>/", TaskProgressConsumer.as_asgi()),
    path("task/progress/<str:taskID>/", TaskProgressConsumer.as_asgi()),

]
