# magazine/views.py
from django.http import JsonResponse
from .models import Cover

def covers_list(request):
    covers = Cover.objects.all().order_by('-issue_date')
    data = [cover.as_dict() for cover in covers]
    return JsonResponse(data, safe=False)

def cover_detail(request, cover_id):
    try:
        cover = Cover.objects.get(pk=cover_id)
        return JsonResponse(cover.as_dict())
    except Cover.DoesNotExist:
        return JsonResponse({'error': 'Cover not found'}, status=404)
