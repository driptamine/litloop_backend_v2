import json
import sys
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user", AnonymousUser())
        sys.stderr.write(f"DEBUG NotificationConsumer: user={user} is_authenticated={user.is_authenticated}\n")
        sys.stderr.flush()
        if user.is_authenticated:
            self.user_id = self.scope["user"].id
            self.room_group_name = f'user_{self.user_id}_notifications'

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
        else:
            # Accept first to avoid Daphne crash on close without accept
            await self.accept()
            await self.close(code=4001)

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    # Receive notification from group
    async def send_notification(self, event):
        notification = event['notification']

        # Send notification to WebSocket
        await self.send_json(notification)
