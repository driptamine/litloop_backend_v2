import json
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

User = get_user_model()

@csrf_exempt
@require_POST
def forgot_password_api(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        
        if not email:
            return JsonResponse({'error': 'Email is required'}, status=400)
            
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # We don't want to leak whether an email exists or not
            return JsonResponse({'message': 'If an account exists with this email, a reset link has been generated.'})
            
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # In a real app, this would be the frontend URL
        reset_link = f"/users/password-reset/{uid}/{token}/"
        
        return JsonResponse({
            'message': 'Password reset link generated.',
            'reset_link': reset_link
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def password_reset_confirm_api(request, uidb64, token):
    try:
        data = json.loads(request.body)
        new_password = data.get('new_password')
        
        if not new_password:
            return JsonResponse({'error': 'New password is required'}, status=400)
            
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
            
        if user is not None and default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return JsonResponse({'message': 'Password has been reset successfully.'})
        else:
            return JsonResponse({'error': 'The reset link is invalid or has expired.'}, status=400)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
