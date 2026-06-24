# from __future__ import absolute_import
from django.urls import path
from movies.views import (
    import_watchlist_csv,
    get_watchlist,
    ammy_shuffle_watchlist
)
from movies.views_no_drf import (
    views_up_view,
    add_movie_view,
    feed_movies_view,
    list_movies_view,
    record_movie_impressions,
    movie_like_view,
)

urlpatterns = [
    path('import_watchlist_csv/', import_watchlist_csv, name='import_watchlist_csv'),
    path('watchlist/', get_watchlist),
    path('watchlist/ammy_shuffle/', ammy_shuffle_watchlist),

    path('views/up/', views_up_view, name='views_up'),
    path('add/', add_movie_view, name='add_movie'),
    path('feed/', feed_movies_view, name='feed_movies'),
    path('list/', list_movies_view, name='list_movies'),

    path('impressions/batch/', record_movie_impressions, name='movie-impressions-batch'),
    path('<int:tmdb_id>/like/', movie_like_view, name='movie-like'),
]
