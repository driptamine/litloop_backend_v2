# from __future__ import absolute_import
from django.urls import path

from posts.views.user_posts_no_drf import current_user_posts_view, user_posts_view
from posts.views import (
    create_post,
    PostCreateView,
    create_post_with_photos,
    create_post_with_video,
    create_post_with_line_breaks,
    create_post_with_media,
    create_post_no_drf,
    post_api_view,

    list_of_posts,
    post_detail,
    update_post_no_drf,
    delete_post_no_drf,
)

urlpatterns = [

    # ──────── CREATE POSTS ────────
    path('create/', post_api_view, name="post-create"),
    path('me/', current_user_posts_view, name="my-posts"),
    path('user/<str:username>/', user_posts_view, name="user-posts"),
    path('create/create_post_with_line_breaks',      create_post_with_line_breaks, name="posts"),

    path('create/v4',      create_post, name="posts"),
    path('create/postman', create_post_with_photos, name="posts"),
    path('create/post_with_videos', create_post_with_video, name="posts"),

    
    path('create_post_api/', create_post_with_media, name="posts"),
    path('create_no_drf/', create_post_no_drf, name="create-post-no-drf"),
    path('update_no_drf/<int:post_id>/', update_post_no_drf, name="update-post-no-drf"),
    path('delete_no_drf/<int:post_id>/', delete_post_no_drf, name="delete-post-no-drf"),
    path('list_no_drf/', list_of_posts, name="list-posts-no-drf"),
    path('detail_no_drf/<int:post_id>/', post_detail, name="post-detail-no-drf"),


    # ──────── VIEW POSTS ────────
    path('list/',          list_of_posts, name="posts"),
    path('<int:post_id>/', post_api_view, name='post_detail'),


    # ──────── FEED ────────

    # ──────── MISC ────────
]
