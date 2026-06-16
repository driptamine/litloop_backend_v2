import json, os
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from todos.models import Todo

# Get all todos
def get_todos(request):
    todos = Todo.objects.all()
    data = [todo.to_dict() for todo in todos]

    # print(os.environ.get('ENVIRONMENT'))
    return JsonResponse(data, safe=False)

# Get single todo
def get_todo(request, todo_id):
    try:
        todo = Todo.objects.get(id=todo_id)
        return JsonResponse(todo.to_dict())
    except Todo.DoesNotExist:
        return JsonResponse({"error": "Todo not found"}, status=404)

# Create a todo
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

# Update a todo
@csrf_exempt
def update_todo(request, todo_id):
    if request.method == "PUT":
        try:
            todo = Todo.objects.get(id=todo_id)
            data = json.loads(request.body)
            todo.title = data.get("title", todo.title)
            todo.completed = data.get("completed", todo.completed)
            todo.save()
            return JsonResponse(todo.to_dict())
        except Todo.DoesNotExist:
            return JsonResponse({"error": "Todo not found"}, status=404)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON")
    return HttpResponseBadRequest("Invalid method")

# Delete a todo
@csrf_exempt
def delete_todo(request, todo_id):
    if request.method == "DELETE":
        try:
            todo = Todo.objects.get(id=todo_id)
            todo.delete()
            return JsonResponse({"message": "Todo deleted"})
        except Todo.DoesNotExist:
            return JsonResponse({"error": "Todo not found"}, status=404)
    return HttpResponseBadRequest("Invalid method")
