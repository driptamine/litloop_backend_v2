from django.urls import path
from tracks.views.base_no_drf import (
    track_list_view, 
    track_pagination_view,
    track_all_view,
    search_track_view,
    track_detail_view,
    track_update_view,
    track_delete_view,
)
from videos.upload import s3_views_qalybay
from tracks.upload import gcs_track_views_no_drf as gcs_track_views, gcs_native_track_views_no_drf as gcs_native_track_views

urlpatterns = [
    path('create_presigned_url/', s3_views_qalybay.create_presigned_url  ),
    path('get_presigned_url/', s3_views_qalybay.get_presigned_url  ),
    path('complete_upload/', s3_views_qalybay.complete_upload  ),

    # GCS Upload Endpoints (Matches S3 Flow via Boto3/HMAC)
    path('gcs/create_presigned_url/', gcs_track_views.gcs_initiate_track_upload, name='gcs_initiate_track'),
    path('gcs/get_presigned_url/', gcs_track_views.gcs_get_track_part_url, name='gcs_get_track_part'),
    path('gcs/complete_upload/', gcs_track_views.gcs_complete_track_upload, name='gcs_complete_track'),

    # Native GCS Upload Endpoints (Using google-cloud-storage library)
    path('gcs/native/initiate/', gcs_native_track_views.gcs_native_initiate_track_upload, name='gcs_native_initiate_track'),
    path('gcs/native/complete/', gcs_native_track_views.gcs_native_complete_track_upload, name='gcs_native_complete_track'),

    path('', track_pagination_view, name="tracks_list"),
    path('all', track_all_view, name="tracks_all"),
    path('search', search_track_view, name="search"),

    # PK patterns must come before string patterns to avoid collisions
    path('<int:pk>/upd/', track_update_view, name="track_update_pk"),
    path('<str:track_uri>/upd/', track_update_view, name="track_update"),
    
    path('<int:pk>/del/', track_delete_view, name="track_delete_pk"),
    path('<str:track_uri>/del/', track_delete_view, name="track_delete"),
    
    path('<int:pk>/', track_detail_view, name="track_detail_pk"),
    path('<str:track_uri>/', track_detail_view, name="track_detail"),
]
