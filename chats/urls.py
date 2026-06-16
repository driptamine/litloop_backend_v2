from django.urls import path
from chats.views import (
    chat_list, chat_detail, send_message, chat_with_gemini, 
    create_chat, get_or_create_direct_chat, my_chats, delete_chat, mark_as_read,
    upload_chat_attachment, get_ice_servers_api, voice_message_upload_api
)

urlpatterns = [
    # VoIP / WebRTC
    path('ice_servers/', get_ice_servers_api, name='ice_servers'),

    # Voice Messages
    path('voice/upload/', voice_message_upload_api, name='voice_upload'),

    # Room Management
    path('', chat_list, name='chat_list'),
    path('me/', my_chats, name='my_chats'),
    path('create/', create_chat, name='create_chat'),
    path('<int:chat_id>/', chat_detail, name='chat_detail'),
    path('<int:chat_id>/read/', mark_as_read, name='mark_as_read'),
    path('<int:chat_id>/read', mark_as_read),
    path('<int:chat_id>/delete/', delete_chat, name='delete_chat'),
    path('<int:chat_id>/delete', delete_chat),
    path('<int:chat_id>/send/', send_message, name='send_message'),
    path('<int:chat_id>/send', send_message),
    
    # Upload
    path('upload/', upload_chat_attachment, name='chat_upload_attachment'),
    
    # User-to-User DM approach
    path('u/<int:user_id>/', get_or_create_direct_chat, name='user_direct_chat'),
    
    # AI Assistant
    path("gemini/", chat_with_gemini, name='chat_with_gemini'),
]
