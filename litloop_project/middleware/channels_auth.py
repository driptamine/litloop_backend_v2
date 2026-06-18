from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from users.jwt_auth import decode_jwt
from users.models import User
from urllib.parse import parse_qs

class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token", [None])[0]

        if token:
            user = await self.get_user(token)
            scope["user"] = user
        else:
            if "user" not in scope:
                scope["user"] = AnonymousUser()

        return await self.inner(scope, receive, send)

    @database_sync_to_async
    def get_user(self, token):
        try:
            payload = decode_jwt(token)
            if not payload:
                return AnonymousUser()

            user_id = payload.get("user_id")
            if not user_id:
                return AnonymousUser()

            return User.objects.get(id=user_id)
        except (User.DoesNotExist, Exception):
            return AnonymousUser()
