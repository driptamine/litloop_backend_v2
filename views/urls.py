# from __future__ import absolute_import
from django.urls import path
from views.views import (
    ViewsUP
)
from views.views_no_drf import memes_view


urlpatterns = [

    path('up', ViewsUP.as_view()),
    path('memes', memes_view)

]
