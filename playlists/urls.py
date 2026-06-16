from django.urls import path
from playlists.views.base import (
    PlaylistListView,
    playlist_detail,
    playlist_offset,
)

urlpatterns = [
    path('', PlaylistListView.as_view(), name="playlist_list"),
    path('<str:playlist_uri>/', playlist_detail, name="playlist_detail"),
    path('<str:playlist_uri>/tracks', playlist_offset, name="playlist_tracks"),
]
