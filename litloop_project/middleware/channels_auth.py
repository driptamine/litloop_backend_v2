from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from users.jwt_auth import decode_jwt
from users.models import User
from urllib.parse import parse_qs

class JWTAuthMiddleware:
    """
    Custom middleware to authenticate WebSocket connections via JWT token in query string.
    Expected URL: ws://localhost:8000/ws/chat/1/?token=<jwt_token>
    """
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Extract token from query string
        raw_qs = scope.get("query_string", b"")
        print(f"DEBUG: raw query_string={raw_qs!r}")
        query_string = raw_qs.decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token", [None])[0]

        if token:
            print(f"DEBUG: Found token in query string: {token[:20]}...")
            user = await self.get_user(token)
            print(f"DEBUG: Authenticated user: {user}")
            scope["user"] = user
        else:
            print("DEBUG: No token found in query string")
            # If no token, check if user is already in scope (e.g. from session)
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
