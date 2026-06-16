import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from users.auth_utils import jwt_required_testable
from .services import StorageService

@csrf_exempt
@jwt_required_testable
def presigned_url_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    file_path = data.get('file_path')
    file_type = data.get('file_type')
    provider = data.get('provider', 's3')

    if not file_path or not file_type:
        return JsonResponse({'error': 'file_path and file_type are required'}, status=400)

    try:
        response_data = StorageService.get_presigned_url(
            file_path=file_path,
            file_type=file_type,
            provider=provider
        )
        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
