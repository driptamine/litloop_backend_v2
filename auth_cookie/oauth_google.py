import json
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
from django.conf import settings
from .services import google_get_access_token

@method_decorator(csrf_exempt, name='dispatch')
class GoogleLoginApi(View):
    def put(self, request):
        try:
            data = json.loads(request.body)
            code = data.get('code', False)
            # redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI
            # Get origin from request headers
            origin = request.META.get('HTTP_ORIGIN', '')
            if origin == 'https://litloop.netlify.app':
                print('origin - ', origin)
                redirect_uri = "https://litloop.netlify.app/auth/google/callback"
            else:

                redirect_uri = "http://localhost:3001/auth/google/callback"
                print('origin - ', origin)

            access_token = google_get_access_token(code=code, redirect_uri=redirect_uri)
            return JsonResponse(access_token, safe=False)

        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
