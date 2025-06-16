import requests
from django.http import JsonResponse

def get_suggestions(request):
    query_text = request.GET.get('q')
    cursor_position = request.GET.get('cp')  # Optional, not used in this example

    if not query_text:
        return JsonResponse({'error': 'Missing query parameter `q`'}, status=400)

    url = "https://www.google.com/complete/search"
    params = {
        'client': 'firefox',
        'q': query_text,
        'hl': 'en-US',
        'dpr': '1.5',
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return JsonResponse({'error': 'Failed to fetch suggestions', 'details': str(e)}, status=500)

    output = {
        "results": [{"query": item} for item in data[1]]
    }

    return JsonResponse(output)
