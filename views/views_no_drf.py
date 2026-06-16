import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from views.tasks import process_view

@csrf_exempt
def views_up_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    
    # Try POST data first, then JSON body
    user_id = request.POST.get('user_id')
    post_id = request.POST.get('post_id')
    
    if not user_id or not post_id:
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            post_id = data.get('post_id')
        except:
            pass
            
    if not user_id or not post_id:
        return JsonResponse({'error': 'user_id and post_id are required'}, status=400)

    result = process_view.delay(user_id, post_id)
    return HttpResponse(f'View Accepted {result.id}')
