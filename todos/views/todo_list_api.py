# views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from todos.models import Todo

@login_required
def todo_list_api(request):
    user = request.user
    todos_qs = Todo.objects.filter(user=user)

    todos = []
    for todo in todos_qs:
        todos.append({
            'id': todo.id,
            'title': todo.title,
            'is_done': todo.is_done,
        })

    background_image_url = None
    if hasattr(user, 'profile') and user.profile.background_image:
        background_image_url = user.profile.background_image.url

    data = {
        'todos': todos,
        'background_image_url': background_image_url
    }

    return JsonResponse(data)
