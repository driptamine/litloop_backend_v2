from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

from uploader.channels import TaskProgressConsumer
from chats.consumers import ChatConsumer
from notifications.consumers import NotificationConsumer

# from users import views as users_views
# from posts import views as posts_views

# from django.db.models.loading import cache as model_cache
# if not model_cache.loaded:
#     model_cache.get_models()

# from uploader.websocket.websocket_views import GetHitmen, StartNewHitJob, ScheduleNewHitJob, CreateUserView

from posts.views.user_posts_no_drf import user_posts_view
from litloop_project.maintenance_views import (
    DeleteAllTablesView, RegenerateAllView, 
    DeleteUserTablesView, RegenerateUserTablesView,
    DeleteChatTablesView, RegenerateChatTablesView
)

urlpatterns = [
    # Maintenance endpoints
    path('maintenance/delete-tables/', DeleteAllTablesView.as_view(), name='maintenance-delete-tables'),
    path('maintenance/regenerate/', RegenerateAllView.as_view(), name='maintenance-regenerate'),
    
    path('maintenance/delete-user-tables/', DeleteUserTablesView.as_view(), name='maintenance-delete-user-tables'),
    path('maintenance/regenerate-user-tables/', RegenerateUserTablesView.as_view(), name='maintenance-regenerate-user-tables'),
    
    path('maintenance/delete-chat-tables/', DeleteChatTablesView.as_view(), name='maintenance-delete-chat-tables'),
    path('maintenance/regenerate-chat-tables/', RegenerateChatTablesView.as_view(), name='maintenance-regenerate-chat-tables'),

    # path('/', include('media.urls')),
    path('admin/', admin.site.urls),
    path('auth/', include('auth_cookie.urls')),

    path('ws/', include("uploader.urls", namespace='websocket')),

    path('users/', include('users.urls')),
    path('videos/', include('videos.urls')),

    # path('media/', include('media.urls')),

    path('posts/', include('posts.urls')),
    path('artist/', include('artists.urls')),
    path('album/', include('albums.urls')),
    path('tracks/', include('tracks.urls')),
    path('photos/', include('photos.urls')),
    path('playlist/', include('playlists.urls')),
    path('views/', include('views.urls')),
    path('movies/', include('movies.urls')),

    path('queries/', include('queries.urls')),
    path('websites/', include('websites.urls')),
    path('chats/', include('chats.urls')),
    path('jobs/', include('jobs.urls')),

    path('comments/', include('comments.urls')),

    path('links/', include('links.urls')),
    path('notes/', include('notes.urls')),
    path('todos/', include('todos.urls')),

    path('<str:username>/posts/', user_posts_view, name='user-username-posts'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ref docker-celery
websocket_urlpatterns = [
    # path("task/upload/<str:taskID>/", TaskProgressConsumer.as_asgi()),
    # path("task/transcoding/<str:taskID>/", TaskProgressConsumer.as_asgi()),

    path("task/progress/<str:taskID>/", TaskProgressConsumer.as_asgi()),
    path("ws/chat/<int:chat_id>/", ChatConsumer.as_asgi()),
    path("ws/notifications/", NotificationConsumer.as_asgi()),
]
