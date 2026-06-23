import json
from django.db import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from posts.models import Post, PostImpression
from posts.serializers_no_drf import serialize_post, handle_media_linking
from users.auth_utils import jwt_required_testable, jwt_optional

@csrf_exempt
@jwt_required_testable
def create_post_no_drf(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

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

@csrf_exempt
@jwt_required_testable
def update_post_no_drf(request, post_id):
    if request.method not in ['PUT', 'PATCH']:
        return JsonResponse({'error': f'Method {request.method} not allowed'}, status=405)

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

    # In PATCH/PUT, handle_media_linking with clear_existing=True replaces links if provided
    handle_media_linking(post, data, clear_existing=True)

    return JsonResponse(serialize_post(post, request))

@csrf_exempt
@jwt_required_testable
def delete_post_no_drf(request, post_id):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Only DELETE allowed'}, status=405)

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)

    if post.author != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    post.delete()
    return JsonResponse({'message': 'Post deleted'}, status=204)

@jwt_optional
def list_of_posts(request):
    posts = Post.objects.all().order_by('-created_at')
    # Use paginate_queryset if available, otherwise simple list
    data = [serialize_post(post, request) for post in posts]
    return JsonResponse({'posts': data})

@jwt_optional
def post_detail(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        return JsonResponse(serialize_post(post, request))
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)


@csrf_exempt
@jwt_required_testable
def record_post_impressions(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    post_ids = data.get('post_ids', [])
    if not post_ids or not isinstance(post_ids, list):
        return JsonResponse({'error': 'post_ids must be a non-empty list'}, status=400)

    user = request.user
    recorded = 0
    for post_id in post_ids:
        try:
            post = Post.objects.get(id=post_id)
            PostImpression.objects.create(post=post, user=user)
            Post.objects.filter(id=post_id).update(impressions_count=models.F('impressions_count') + 1)
            recorded += 1
        except Post.DoesNotExist:
            continue

    return JsonResponse({'status': 'ok', 'recorded': recorded})
