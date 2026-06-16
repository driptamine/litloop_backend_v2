import json
from django.conf import settings
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from posts.models import Post
from posts.serializers_no_drf import serialize_post, handle_media_linking
from users.auth_utils import jwt_required, jwt_required_testable, jwt_optional

@csrf_exempt
@jwt_optional
def post_api_view(request, post_id=None):
    if request.method == 'GET':
        if not post_id:
            return JsonResponse({'error': 'Post ID required'}, status=400)
        try:
            post = Post.objects.get(id=post_id)
            return JsonResponse(serialize_post(post, request))
        except Post.DoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=404)

    # All other methods require authentication
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        post = Post.objects.create(
            author=request.user,
            title=data.get('title'),
            description=data.get('description', '')
        )
        handle_media_linking(post, data)
        return JsonResponse(serialize_post(post, request), status=201)

    elif request.method in ['PUT', 'PATCH']:
        if not post_id:
            return JsonResponse({'error': 'Post ID required'}, status=400)
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=404)

        if post.author != request.user:
            return JsonResponse({'error': 'Permission denied'}, status=403)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if 'title' in data:
            post.title = data['title']
        if 'description' in data:
            post.description = data['description']
        post.save()

        handle_media_linking(post, data, clear_existing=True)
        return JsonResponse(serialize_post(post, request))

    elif request.method == 'DELETE':
        if not post_id:
            return JsonResponse({'error': 'Post ID required'}, status=400)
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=404)

        if post.author != request.user:
            return JsonResponse({'error': 'Permission denied'}, status=403)

        post.delete()
        return JsonResponse({'message': 'Post deleted'}, status=204)

    return JsonResponse({'error': f'Method {request.method} not allowed'}, status=405)
