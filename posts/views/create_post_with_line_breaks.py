import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from posts.models import Post

@csrf_exempt
def create_post_with_line_breaks(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        description = data.get('description', '')

        if description.strip():
            # Replace newlines with <br/> tags
            formatted_content = description.replace('\n', '<br/>')
            post = Post.objects.create(description=formatted_content)
            return JsonResponse({'content': formatted_content}, status=201)
        else:
            return JsonResponse({'error': 'Empty content'}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)
