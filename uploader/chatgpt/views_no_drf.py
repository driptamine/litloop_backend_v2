from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Video

@csrf_exempt
def chunked_upload_view(request):
    if request.method != 'PUT':
        return JsonResponse({'error': 'Only PUT allowed'}, status=405)
    
    if not request.FILES.get('file'):
        return JsonResponse({'error': 'No file uploaded'}, status=400)

    file_obj = request.FILES['file']
    video = Video.objects.create(video_file=file_obj)
    return JsonResponse({'video_id': video.id}, status=201)
