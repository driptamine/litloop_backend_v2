# from __future__ import absolute_import
from django.urls import path
from movies.views import (
    import_watchlist_csv,
    import_ratings_csv,
    get_watchlist,
    user_watchlist_by_username,
    user_ratings_by_username,
    ammy_shuffle_watchlist
)
from movies.views_no_drf import (
    views_up_view,
    add_movie_view,
    feed_movies_view,
    list_movies_view,
    list_imdbmovies_view,
    imdb_movie_detail_view,
    record_movie_impressions,
    movie_like_view,
    movie_detail_view,
)

urlpatterns = [
    path('import_watchlist_csv/', import_watchlist_csv, name='import_watchlist_csv'),
    path('import_ratings_csv/', import_ratings_csv, name='import_ratings_csv'),

    path('watchlist/', get_watchlist),
    path('watchlist/ammy_shuffle/', ammy_shuffle_watchlist),
    
    path('<str:username>/watchlist/', user_watchlist_by_username),
    path('<str:username>/ratings/', user_ratings_by_username),

    path('views/up/', views_up_view, name='views_up'),
    path('add/', add_movie_view, name='add_movie'),
    path('feed/', feed_movies_view, name='feed_movies'),
    path('list/', list_movies_view, name='list_movies'),
    path('imdbmovies/list/', list_imdbmovies_view, name='list_imdbmovies'),
    path('imdbmovies/<str:imdb_id>/', imdb_movie_detail_view, name='imdb-movie-detail'),

    path('impressions/batch/', record_movie_impressions, name='movie-impressions-batch'),
    path('<int:tmdb_id>/like/', movie_like_view, name='movie-like'),
    path('<int:movie_id>/', movie_detail_view, name='movie-detail'),
]
