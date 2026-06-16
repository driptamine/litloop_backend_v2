from rest_framework import generics, permissions
from posts.models import Post
from posts.serializers import PostSerializer

class CurrentUserPostsListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user).order_by('-created_at')
