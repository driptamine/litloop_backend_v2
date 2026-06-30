from django.urls import path
from memes.views import memes_list_view, memes_list_db_view


urlpatterns = [
    path('', memes_list_view),
    path('list', memes_list_db_view),
]
