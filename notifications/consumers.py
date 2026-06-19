import logging

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user_id = None
        self.room_group_name = None
        self.authenticated = False

        await self.accept()

        user = self.scope.get("user", AnonymousUser())
        if user.is_authenticated:
            await self._join_user_group(user.id)

    async def disconnect(self, close_code):
        if self.room_group_name:
            try:
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )
            except Exception:
                logger.exception("Failed to leave notification group %s", self.room_group_name)

    async def receive_json(self, content):
        if content.get('type') == 'auth':
            await self._handle_auth(content)

    async def _join_user_group(self, user_id):
        self.authenticated = True
        self.user_id = user_id
        self.room_group_name = f'user_{self.user_id}_notifications'
        try:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
        except Exception:
            logger.exception("Failed to join notification group %s (is Redis running?)", self.room_group_name)
            await self.send_json({'type': 'error', 'message': 'notification_service_unavailable'})

    async def _handle_auth(self, content):
        token = content.get('token')
        if not token or self.authenticated:
            return

        user = await self._get_user_from_token(token)
        if user and user.is_authenticated:
            await self._join_user_group(user.id)
            await self.send_json({'type': 'auth_ok'})

    @database_sync_to_async
    def _get_user_from_token(self, token):
        from users.jwt_auth import decode_jwt
        from users.models import User
        try:
            payload = decode_jwt(token)
            if payload:
                user_id = payload.get('user_id')
                if user_id:
                    return User.objects.get(id=user_id)
        except Exception:
            pass
        return AnonymousUser()

    async def send_notification(self, event):
        notification = event['notification']
        await self.send_json(notification)
