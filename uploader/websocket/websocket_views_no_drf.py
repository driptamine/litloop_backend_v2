import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from dateutil import parser
from users.auth_utils import jwt_required_testable
from .websocket_task import start_new_hit_job

UserModel = get_user_model()

@jwt_required_testable
def get_hitmen_view(request):
    return JsonResponse({"names": ["bill", "bob", "keanu", "logan"]})

@csrf_exempt
def start_new_hit_job_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
    name = data.get("target_name")
    if not name:
        return JsonResponse({'error': 'target_name is required'}, status=400)

    new_celery_task = start_new_hit_job.delay(name)
    return JsonResponse({
        "result": f"Job created for {name}",
        "celery_task_id": new_celery_task.id,
    })

@csrf_exempt
def schedule_new_hit_job_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    name = data.get("target_name")
    schedule_time_str = data.get("schedule_time")
    days_of_week = data.get("days_of_week")

    if not name or not schedule_time_str or not days_of_week:
        return JsonResponse({'error': 'target_name, schedule_time, and days_of_week are required'}, status=400)

    schedule_time = parser.parse(schedule_time_str)
    schedule, _ = CrontabSchedule.objects.get_or_create(
        day_of_week=",".join(days_of_week),
        minute=schedule_time.minute,
        hour=schedule_time.hour,
    )

    PeriodicTask.objects.update_or_create(
        name=f"Schedule hit job for {name}",
        defaults={
            "task": "uploader.websocket.websocket_task.start_new_hit_job", # Fixed task path
            "args": json.dumps([name]),
            "crontab": schedule,
        },
    )

    return JsonResponse({"result": f"Task scheduled for execution"})

@csrf_exempt
def create_user_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not password:
        return JsonResponse({'error': 'Password is required'}, status=400)

    if not email:
        return JsonResponse({'error': 'Email is required'}, status=400)

    if not username:
        # Use email prefix as username
        username = email.split('@')[0].replace('.', '_')
        
    # Handle username collision
    base_username = username
    counter = 1
    while UserModel.objects.filter(username=username).exists():
        import random
        username = f"{base_username}{random.randint(100, 999)}"
        if counter > 10:
            break
        counter += 1

    user = UserModel.objects.create_user(username=username, password=password, email=email)
    return JsonResponse({
        'id': user.id,
        'username': user.username,
        'email': user.email
    }, status=201)
