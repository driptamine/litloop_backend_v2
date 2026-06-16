from django.http import JsonResponse, Http404
from notes.models import Page
from notes.serializers import serialize_page

def get_page(request, page_id):
    try:
        page = Page.objects.prefetch_related('blocks', 'children').get(pk=page_id)
    except Page.DoesNotExist:
        raise Http404("Page not found")

    data = serialize_page(page)
    return JsonResponse(data, safe=False)
