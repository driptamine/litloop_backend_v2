import json, jwt, datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate

from users.jwt_auth import generate_jwt, decode_jwt
from users.models import User



def cookie_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user = authenticate(username=data['username'], password=data['password'])
        if user:
            payload = {
                'id': user.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
                'iat': datetime.datetime.utcnow()
            }

            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

            res = JsonResponse({'message': 'Logged in'})
            res.set_cookie(
                key='jwt',
                value=token,
                httponly=True,
                samesite='Lax'
            )
            return res
        return JsonResponse({'error': 'Invalid credentials'}, status=401)
