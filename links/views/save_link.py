import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from links.models import Link, Hashtag, LinkTag
from users.models import User  # adjust if your user model is imported differently

@csrf_exempt
def save_link(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST allowed")

    try:
        data    = json.loads(request.body)
        url     = data.get("url")
        tags    = data.get("tags", [])
        user_id = data.get("user_id")  # optional user

        if not url:
            return JsonResponse({"error": "URL is required"}, status=400)

        # Optional: attach a user
        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return JsonResponse({"error": "Invalid user ID"}, status=400)

        # Create the link
        link = Link.objects.create(url=url, user=user)

        # Create or get hashtags and add them through LinkTag
        for tag_name in tags:
            tag_name = tag_name.strip().lower()
            if not tag_name:
                continue
            hashtag, _ = Hashtag.objects.get_or_create(name=tag_name)
            LinkTag.objects.get_or_create(link=link, hashtag=hashtag)

        return JsonResponse({"success": True, "link_id": link.id})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
