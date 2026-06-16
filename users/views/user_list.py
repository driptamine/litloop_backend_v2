import json, jwt, datetime

from django.http import JsonResponse
from users.models import User


def userlist(request):

    users = User.objects.all()

    user_data = []
    for user in users:
        user_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'avatar': user.avatar,
        })

    data = {
        'count': users.count(),
        'results': user_data
    }
    return JsonResponse(data)
