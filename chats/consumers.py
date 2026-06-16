import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Chat, Message, VoiceMessage
from users.models import User

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'

        print(f"DEBUG: WebSocket connect attempt - User: {self.user}, Chat ID: {self.chat_id}")

        if not self.user.is_authenticated:
            print("DEBUG: Connection rejected - User not authenticated")
            await self.close()
            return

        # Auto-add user to participants and verify chat exists
        success = await self.add_to_participants(self.chat_id, self.user.id)
        if not success:
            print(f"DEBUG: Connection rejected - Chat {self.chat_id} not found or error adding participant")
            await self.close()
            return
        
        print(f"DEBUG: Connection accepted for user {self.user.id} in chat {self.chat_id}")

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    # Receive message from WebSocket
    async def receive_json(self, content):
        msg_type = content.get('type', 'chat_message')
        
        if msg_type == 'chat_message':
            text = content.get('text', '')
            attachments = content.get('attachments', [])
            voice_message_id = content.get('voice_message_id')
            
            if not text and not attachments and not voice_message_id:
                return

            # Save message to database
            message_data = await self.save_message(self.chat_id, self.user.id, text, attachments, voice_message_id)

            if 'error' in message_data:
                print(f"DEBUG: Error saving message: {message_data['error']}")
                await self.send_json(message_data)
                return

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message_data
                }
            )

            # Trigger notifications for other participants
            notifications = await self.create_notifications(self.chat_id, self.user.id, message_data['id'])
            for n in notifications:
                await self.channel_layer.group_send(
                    f'user_{n["user_id"]}_notifications',
                    {
                        'type': 'send_notification',
                        'notification': n['data']
                    }
                )
        
        elif msg_type.startswith('voip_'):
            # Handle VoIP signaling
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'voip_signal',
                    'sender_id': self.user.id,
                    'content': content
                }
            )
            
            # Optionally track call state in DB
            if msg_type == 'voip_call_start':
                await self.db_track_call_start(content)
                
                # Send "Incoming Call" notification to participants global channels
                participants_ids = await self.get_participants_ids(self.chat_id, self.user.id)
                for p_id in participants_ids:
                    await self.channel_layer.group_send(
                        f'user_{p_id}_notifications',
                        {
                            'type': 'send_notification',
                            'notification': {
                                'type': 'incoming_call',
                                'chat_id': self.chat_id,
                                'caller_id': self.user.id,
                                'caller_name': self.user.username,
                                'caller_avatar': self.user.avatar if hasattr(self.user, 'avatar') else None,
                                'call_type': content.get('call_type', 'voice')
                            }
                        }
                    )
            elif msg_type == 'voip_call_accept':
                await self.db_track_call_status(self.chat_id, 'ongoing')
            elif msg_type == 'voip_call_reject':
                await self.db_track_call_status(self.chat_id, 'rejected')
            elif msg_type == 'voip_call_end':
                await self.db_track_call_end(content)

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send_json({
            'type': 'new_message',
            'message': message
        })

    async def voip_signal(self, event):
        # Don't send signal back to sender
        if event['sender_id'] != self.user.id:
            await self.send_json(event['content'])

    @database_sync_to_async
    def get_participants_ids(self, chat_id, exclude_user_id):
        try:
            chat = Chat.objects.get(id=chat_id)
            return list(chat.participants.exclude(id=exclude_user_id).values_list('id', flat=True))
        except Exception:
            return []

    @database_sync_to_async
    def db_track_call_start(self, content):
        from .models import Call, Chat
        try:
            chat = Chat.objects.get(id=self.chat_id)
            Call.objects.create(
                chat=chat,
                caller=self.user,
                call_type=content.get('call_type', 'voice'),
                status='initiated'
            )
        except Exception as e:
            print(f"Error tracking call start: {e}")

    @database_sync_to_async
    def db_track_call_status(self, chat_id, status):
        from .models import Call
        try:
            call = Call.objects.filter(chat_id=chat_id, status__in=['initiated', 'ongoing']).last()
            if call:
                call.status = status
                call.save()
        except Exception as e:
            print(f"Error tracking call status: {e}")

    @database_sync_to_async
    def db_track_call_end(self, content):
        from .models import Call
        from django.utils import timezone
        try:
            call = Call.objects.filter(chat_id=self.chat_id, status__in=['initiated', 'ongoing']).last()
            if call:
                call.status = 'completed'
                call.ended_at = timezone.now()
                call.save()
        except Exception as e:
            print(f"Error tracking call end: {e}")

    @database_sync_to_async
    def add_to_participants(self, chat_id, user_id):
        try:
            chat = Chat.objects.get(id=chat_id)
            user = User.objects.get(id=user_id)
            if not chat.participants.filter(id=user_id).exists():
                chat.participants.add(user)
            return True
        except Exception as e:
            print(f"DEBUG: Error adding participant: {e}")
            return False

    @database_sync_to_async
    def create_notifications(self, chat_id, sender_id, message_id):
        from notifications.models import Notification
        from django.contrib.contenttypes.models import ContentType
        
        try:
            chat = Chat.objects.get(id=chat_id)
            message = Message.objects.get(id=message_id)
            sender = User.objects.get(id=sender_id)
            
            participants = chat.participants.exclude(id=sender_id)
            content_type = ContentType.objects.get_for_model(message)
            
            notifications_data = []
            for p in participants:
                Notification.objects.create(
                    from_user=sender,
                    to_user=p,
                    target_content_type=content_type,
                    target_object_id=message.id
                )
                unread_count = chat.messages.exclude(user=p).filter(is_read=False).count()
                
                voice = message.voice_messages.first()
                if message.text:
                    preview = message.text[:50]
                elif voice:
                    preview = "[Voice Message]"
                elif message.attachments:
                    preview = f"[{message.attachments[0].get('type', 'attachment')}]"
                else:
                    preview = ""

                notifications_data.append({
                    'user_id': p.id,
                    'data': {
                        'type': 'new_message',
                        'chat_id': chat_id,
                        'chat_user_id': sender.id,
                        'message_id': message_id,
                        'preview': preview,
                        'sender': sender.username,
                        'text': preview,
                        'unread_count': unread_count,
                        'created_at': message.created_at.isoformat()
                    }
                })
            return notifications_data
        except Exception as e:
            print(f"Error creating notifications: {e}")
            return []

    @database_sync_to_async
    def save_message(self, chat_id, user_id, text, attachments=None, voice_message_id=None):
        try:
            chat = Chat.objects.get(id=chat_id)
            user = User.objects.get(id=user_id) if user_id else None
            
            message = Message.objects.create(
                chat=chat,
                user=user,
                text=text,
                attachments=attachments or []
            )

            voice_data = None
            if voice_message_id:
                try:
                    voice = VoiceMessage.objects.get(id=voice_message_id)
                    message.voice_messages.add(voice)
                    voice_data = {
                        'id': voice.id,
                        'url': voice.url,
                        'duration': voice.duration
                    }
                except VoiceMessage.DoesNotExist:
                    pass
            
            return {
                'id': message.id,
                'text': message.text,
                'username': user.username if user else 'AI',
                'avatar': user.avatar if user else None,
                'created_at': message.created_at.isoformat(),
                'is_read': message.is_read,
                'attachments': message.attachments,
                'voice_message': voice_data
            }
        except Exception as e:
            return {'error': str(e)}
