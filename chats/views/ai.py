import os
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from ..models import Chat, Message
from .common import get_authenticated_user

try:
    from google import genai
    client = genai.Client(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))
except ImportError:
    client = None


@csrf_exempt
@require_GET
def chat_with_gemini(request):
    """AI Chat view that persists messages to the database."""
    user_query = request.GET.get("q", "").strip()

    if not user_query:
        return HttpResponseBadRequest("Missing 'q' query parameter.")

    if not client:
        return JsonResponse({"error": "Gemini client not configured"}, status=500)

    try:
        gemini_chat, _ = Chat.objects.get_or_create(
            name="gemini-ai",
            defaults={"description": "AI Assistant Conversation"}
        )

        user = get_authenticated_user(request)
        Message.objects.create(
            chat=gemini_chat,
            user=user,
            text=user_query
        )

        response = client.models.generate_content(
            contents=user_query,
            model='gemini-2.0-flash-001'
        )
        ai_text = response.text

        Message.objects.create(
            chat=gemini_chat,
            text=ai_text
        )

        return JsonResponse({
            "response": ai_text
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
