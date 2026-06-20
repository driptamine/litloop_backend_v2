from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..utils import get_ice_servers


@csrf_exempt
def get_ice_servers_api(request):
    """
    API endpoint to retrieve ICE servers for WebRTC.
    """
    return JsonResponse({
        "ice_servers": get_ice_servers()
    })
