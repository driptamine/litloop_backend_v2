from django.urls import path
from artists.views.base_no_drf import (
    artist_list_view,
    artist_pagination_view,
    artist_all_view,
    search_artist_view,
    artist_detail_view,
    artist_albums_view,
)

urlpatterns = [
    path('', artist_pagination_view, name="artists_list"),
    path('all', artist_all_view, name="artists_all"),
    path('search', search_artist_view, name="search"),
    path('<str:artist_uri>/upd', artist_detail_view, name="artist_detail_upd"),
    path('<str:artist_uri>/', artist_detail_view, name="artist_detail"),
    path('<str:artist_uri>/albums/upd', artist_albums_view, name="artist_albums_upd"),
    path('<str:artist_uri>/albums/', artist_albums_view, name="artist_albums"),
]
