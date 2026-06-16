import json, os
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from todos.models import Todo

@csrf_exempt
def create_todo(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            todo = Todo.objects.create(
                title=data.get("title", ""),
                completed=data.get("completed", False)
            )
            return JsonResponse(todo.to_dict(), status=201)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON")
    return HttpResponseBadRequest("Invalid method")
