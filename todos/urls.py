from django.urls import path
from todos.views import (
    get_todos,
    get_todo,
    create_todo,
    update_todo,
    delete_todo,

)

urlpatterns = [
    path('all', get_todos, name='get_todos'),
    path('<int:todo_id>/', get_todo, name='get_todo'),
    path('create/', create_todo, name='create_todo'),
    path('<int:todo_id>/update/', update_todo, name='update_todo'),
    path('<int:todo_id>/delete/', delete_todo, name='delete_todo'),
]
