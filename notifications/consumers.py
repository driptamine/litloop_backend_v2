import logging
import functools
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from channels.exceptions import StopConsumer
from channels.layers import get_channel_layer
from channels.utils import await_many_dispatch
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def __call__(self, scope, receive, send):
        self.scope = scope
        self.channel_layer = get_channel_layer(self.channel_layer_alias)
        if self.channel_layer is not None:
            try:
                self.channel_name = await self.channel_layer.new_channel()
            except Exception as e:
                logger.error(f"Failed to create channel: {e}")
                self.channel_layer = None
        if self.channel_layer is not None:
            self.channel_receive = functools.partial(
                self.channel_layer.receive, self.channel_name
            )
        if self._sync:
            self.base_send = async_to_sync(send)
        else:
            self.base_send = send
        try:
            if self.channel_layer is not None:
                await await_many_dispatch(
                    [receive, self._safe_channel_receive], self.dispatch
                )
            else:
                await await_many_dispatch([receive], self.dispatch)
        except StopConsumer:
            pass

    async def _safe_channel_receive(self):
        try:
            return await self.channel_receive()
        except Exception as e:
            logger.error(f"Channel layer receive error (swallowed): {e}")
            return None

    async def dispatch(self, message):
        if message is None:
            return
        await super().dispatch(message)

    async def connect(self):
        self.user_id = None
        self.room_group_name = None
        self.authenticated = False

        user = self.scope.get("user", AnonymousUser())
        if user.is_authenticated:
            self.authenticated = True
            self.user_id = user.id
            self.room_group_name = f'user_{self.user_id}_notifications'
            try:
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
            except Exception as e:
                logger.error(f"group_add failed for user {self.user_id}: {e}")

        await self.accept()

    async def disconnect(self, close_code):
        if self.room_group_name:
            try:
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )
            except Exception as e:
                logger.error(f"group_discard failed: {e}")

    async def receive_json(self, content):
        if content.get('type') == 'auth':
            await self._handle_auth(content)

    async def _handle_auth(self, content):
        token = content.get('token')
        if not token or self.authenticated:
            return

        user = await self._get_user_from_token(token)
        if user and user.is_authenticated:
            old_group = self.room_group_name
            self.authenticated = True
            self.user_id = user.id
            self.room_group_name = f'user_{self.user_id}_notifications'
            try:
                if old_group:
                    await self.channel_layer.group_discard(old_group, self.channel_name)
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
            except Exception as e:
                logger.error(f"group op failed during auth for user {self.user_id}: {e}")
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
