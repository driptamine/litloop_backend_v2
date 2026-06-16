from django.urls import path
from albums.views.base_no_drf import (
    album_list_view,
    album_detail_view,
    album_like_view,
    album_pagination_view,
    album_all_view,
    search_album_view,
    feed_view,
)
from views.views_no_drf import views_up_view

urlpatterns = [
    path('', album_pagination_view, name="albums_list"),
    path('all', album_all_view, name="albums_all"),
    path('search', search_album_view, name="search"),
    path('feed/', feed_view, name="feed"),
    path('<str:album_uri>/fike/', album_like_view, name="post"),
    path('<str:album_uri>/upd', album_detail_view, name="album_detail"),
    path('<int:pk>/view/', views_up_view, name='view'),
]
