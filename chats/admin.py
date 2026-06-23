from django.contrib import admin
from .models import Chat, Message, VoiceMessage, Call

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'chat_type', 'is_saved_messages')
    list_filter = ('chat_type', 'is_saved_messages')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'user', 'created_at', 'is_read')

@admin.register(VoiceMessage)
class VoiceMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'duration', 'created_at')

@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'caller', 'call_type', 'status', 'started_at')
