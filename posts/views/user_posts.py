from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404
from users.models import User
from posts.models import Post
from posts.serializers import PostSerializer

class UserPostsListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        return Post.objects.filter(author=user).order_by('-created_at')
