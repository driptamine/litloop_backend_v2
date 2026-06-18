from django.urls import path
from chats.views import (
    chat_list, my_chats, send_message, chat_with_gemini,
    delete_chat, mark_as_read,
    upload_chat_attachment, get_ice_servers_api, voice_message_upload_api,
    # Direct
    direct_chat_list, direct_chat_detail,
    # Group
    group_chat_list, create_group_chat, group_chat_detail,
    group_add_member, group_remove_member,
)

urlpatterns = [
    # VoIP / WebRTC
    path('ice_servers/', get_ice_servers_api, name='ice_servers'),

    # Voice Messages
    path('voice/upload/', voice_message_upload_api, name='voice_upload'),

    # ── Direct Chats ──────────────────────────────────────────────
    path('direct/', direct_chat_list, name='direct_chat_list'),
    path('direct/<int:user_id>/', direct_chat_detail, name='direct_chat_detail'),

    # ── Group Chats ───────────────────────────────────────────────
    path('group/', group_chat_list, name='group_chat_list'),
    path('group/create/', create_group_chat, name='create_group_chat'),
    path('group/<int:chat_id>/', group_chat_detail, name='group_chat_detail'),
    path('group/<int:chat_id>/add/', group_add_member, name='group_add_member'),
    path('group/<int:chat_id>/remove/', group_remove_member, name='group_remove_member'),

    # ── Shared (by chat ID) ──────────────────────────────────────
    path('<int:chat_id>/send/', send_message, name='send_message'),
    path('<int:chat_id>/send', send_message),
    path('<int:chat_id>/read/', mark_as_read, name='mark_as_read'),
    path('<int:chat_id>/read', mark_as_read),
    path('<int:chat_id>/delete/', delete_chat, name='delete_chat'),
    path('<int:chat_id>/delete', delete_chat),

    # Other
    path('me/', my_chats, name='my_chats'),
    path('upload/', upload_chat_attachment, name='chat_upload_attachment'),
    path('', chat_list, name='chat_list'),
    path("gemini/", chat_with_gemini, name='chat_with_gemini'),
]
