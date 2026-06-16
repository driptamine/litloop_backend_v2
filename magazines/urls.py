# magazine/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/covers/', views.covers_list),
    path('api/covers/<int:cover_id>/', views.cover_detail),
    path('api/covers/<int:cover_id>/buy/', views.create_checkout_session),
]
