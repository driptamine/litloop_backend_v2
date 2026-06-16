# from __future__ import absolute_import
from django.urls import path
from notes.views import (
     get_page,
)



urlpatterns = [

    path('<int:page_id>/', get_page, name='page'),


]
