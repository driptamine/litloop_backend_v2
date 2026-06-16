from django.urls import path
from .views_no_drf import (
    comment_list_view,
    comment_detail_view,
    comment_create_view,
    comment_delete_view
)

urlpatterns = [
    path('', comment_list_view, name='comment-list'),
    path('create/', comment_create_view, name='comment-create'),
    path('<uuid:uid>/', comment_detail_view, name='comment-detail'),
    path('<uuid:uid>/delete/', comment_delete_view, name='comment-delete'),
]
