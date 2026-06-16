
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from posts.models import Post
from users.auth_utils import jwt_required

@csrf_exempt  # since no DRF, you might need this if no CSRF token
@jwt_required
def create_post(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data        = json.loads(request.body)
        title       = data.get("title")
        description = data.get("description")

        if not description:
            return JsonResponse({"error": "Missing description"}, status=400)

        post = Post.objects.create(author=request.user, title=title, description=description)

        return JsonResponse({
            "id": post.id,
            "title": post.title,
            "description": post.description,
            "friendly_id": post.friendly_id,
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
