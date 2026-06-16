import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from users.auth_utils import jwt_required_testable
from .models import Comment
from litloop_project.serializers_no_drf import serialize_comment, paginate_queryset, get_paginated_response

def comment_list_view(request):
    queryset = Comment.objects.all().prefetch_related('user')
    
    author_username = request.GET.get('author')
    if author_username:
        queryset = queryset.filter(user__username=author_username)
        
    friendly_token = request.GET.get('friendly_token')
    if friendly_token:
        queryset = queryset.filter(friendly_token=friendly_token)

    items, paginator = paginate_queryset(queryset, request)
    response_data = get_paginated_response(items, paginator, serialize_comment, request)
    return JsonResponse(response_data)

def comment_detail_view(request, uid):
    comment = get_object_or_404(Comment, uid=uid)
    return JsonResponse(serialize_comment(comment, request))

@csrf_exempt
@jwt_required_testable
def comment_create_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    text = data.get('text')
    friendly_token = data.get('friendly_token')
    parent_uid = data.get('parent')

    if not text or not friendly_token:
        return JsonResponse({'error': 'text and friendly_token are required'}, status=400)

    parent = None
    if parent_uid:
        parent = get_object_or_404(Comment, uid=parent_uid)

    comment = Comment.objects.create(
        user=request.user,
        text=text,
        friendly_token=friendly_token,
        parent=parent
    )
    
    return JsonResponse(serialize_comment(comment, request), status=201)

@csrf_exempt
@jwt_required_testable
def comment_delete_view(request, uid):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Only DELETE allowed'}, status=405)
    
    comment = get_object_or_404(Comment, uid=uid)
    
    # Check permissions
    if comment.user != request.user and not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
        
    comment.delete()
    return JsonResponse({}, status=204)
