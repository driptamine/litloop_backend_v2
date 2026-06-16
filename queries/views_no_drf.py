import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def bing_query_view(request):
    query_text = request.GET.get('q', None)
    if not query_text:
        return JsonResponse({'error': 'Missing query parameter q'}, status=400)
        
    api_key = "23c6c54ede484f7c9586245ad7a0fb18"
    url = f"https://api.bing.microsoft.com/v7.0/suggestions?q={query_text}"
    headers = {"Ocp-Apim-Subscription-Key": api_key}

    response = requests.get(url, headers=headers)
    return JsonResponse(response.json())

def brave_query_view(request):
    query_text = request.GET.get('q', None)
    if not query_text:
        return JsonResponse({'error': 'Missing query parameter q'}, status=400)

    api_key = "BSA98IuMyCoiHdPaE05qvoJGk02tod-"
    url = "https://api.search.brave.com/res/v1/suggest/search?count=20"
    headers = {
        "x-subscription-token": api_key,
        'accept': 'application/json',
        'Cache-Control': 'no-cache'
    }

    response = requests.get(url, params={'q': query_text}, headers=headers)
    data = response.json()
    
    return JsonResponse({
        'word': query_text,
        'results': data.get('results', [])
    })

def brave_images_search_view(request):
    query_text = request.GET.get('q', None)
    if not query_text:
        return JsonResponse({'error': 'Missing query parameter q'}, status=400)

    api_key = "BSA98IuMyCoiHdPaE05qvoJGk02tod-"
    url = "https://api.search.brave.com/res/v1/images/search?count=100"
    headers = {
        "x-subscription-token": api_key,
        'accept': 'application/json',
        'Cache-Control': 'no-cache'
    }
    params = {'q': query_text, 'count': '100'}
    
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    
    return JsonResponse({
        'word': query_text,
        'results': data.get('results', [])
    })

def google_firefox_query_view(request):
    query_text = request.GET.get('q', None)
    if not query_text:
        return JsonResponse({'error': 'Missing query parameter q'}, status=400)

    url = "https://www.google.com/complete/search"
    params = {
        'client': 'firefox',
        'q': query_text,
        'hl': 'en-US',
        'dpr': '1.5',
    }
    response = requests.get(url, params=params)
    data = response.json()

    output = {
        "results": [{"query": item} for item in data[1]]
    }
    return JsonResponse(output)

def google_query_view(request):
    query_text = request.GET.get('q', None)
    if not query_text:
        return JsonResponse({'error': 'Missing query parameter q'}, status=400)

    url = "https://www.google.com/complete/search"
    params = {
        'client': 'chrome',
        'q': query_text,
        'hl': 'en-US',
        'dpr': '1.5',
    }
    response = requests.get(url, params=params)
    data = response.json()

    output = {
        "results": [{"query": item} for item in data[1]]
    }
    return JsonResponse(output)
