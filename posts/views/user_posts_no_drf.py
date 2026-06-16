from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from users.models import User
from posts.models import Post
from posts.serializers_no_drf import serialize_post
from users.auth_utils import jwt_required_testable, jwt_optional

@jwt_required_testable
def current_user_posts_view(request):
    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    data = [serialize_post(post, request) for post in posts]
    return JsonResponse(data, safe=False)

@jwt_optional
def user_posts_view(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user).order_by('-created_at')
    data = [serialize_post(post, request) for post in posts]
    return JsonResponse(data, safe=False)
