import os
import requests
from django.http import JsonResponse
from django.views import View
from websites.models import Website, WebsiteImage


class BingWebsiteSearchView(View):
    def get(self, request, *args, **kwargs):
        query_text = request.GET.get('q')
        api_key = os.getenv("BING_API_KEY", "bef3f98862ac4222806c3bfd0ffa9bb6")
        url = f"https://api.bing.microsoft.com/v7.0/search?q={query_text}&cc=en-US&setLang=en&mkt=en-US&count=40"
        headers = {
            "Ocp-Apim-Subscription-Key": api_key
        }

        response = requests.get(url, headers=headers)
        data = response.json()
        results = data.get('webPages', {}).get('value', [])
        return JsonResponse({'results': results})


class BingImageSearchView(View):
    def get(self, request, *args, **kwargs):
        query_text = request.GET.get('q')
        api_key = os.getenv("BING_API_KEY", "bef3f98862ac4222806c3bfd0ffa9bb6")
        url = f"https://api.bing.microsoft.com/v7.0/images/search?q={query_text}&safeSearch=Off"
        headers = {
            "Ocp-Apim-Subscription-Key": api_key
        }

        response = requests.get(url, headers=headers)
        data = response.json()
        results = data.get('value', [])
        return JsonResponse({'results': results})


class BraveWebsiteSearchView(View):
    def get(self, request, *args, **kwargs):
        query_text = request.GET.get('q')

        if "site:" in query_text:
            api_key = os.getenv("BING_API_KEY", "bef3f98862ac4222806c3bfd0ffa9bb6")
            url = f"https://api.bing.microsoft.com/v7.0/search?q={query_text}&cc=en-US&setLang=en&mkt=en-US&count=40"
            headers = {
                "Ocp-Apim-Subscription-Key": api_key
            }

            response = requests.get(url, headers=headers)
            data = response.json()
            results = data.get('webPages', {}).get('value', [])
            return JsonResponse({'results': results})

        api_key = os.getenv("BRAVE_API_KEY", "BSA-7IOG54pS0Xwmc8hw5_L07-Cja3_")
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "x-subscription-token": api_key,
            'accept': 'application/json',
            'Cache-Control': 'no-cache',
            'Accept-Encoding': 'gzip'
        }
        params = {'q': query_text}
        page = request.GET.get('page')
        if page:
            params['offset'] = (int(page) - 1) * 10

        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        results = data.get('web', {}).get('results', [])

        for item in results:
            Website.objects.update_or_create(
                url=item.get('url'),
                defaults={
                    'title': item.get('title'),
                    'body': item.get('description'),
                    'favicon': item.get('favicon'),
                    'query': query_text,
                }
            )

        return JsonResponse({'results': results})


class BraveImageSearchView(View):
    def get(self, request, *args, **kwargs):
        query_text = request.GET.get('q')
        api_key = os.getenv("BRAVE_API_KEY", "BSA-7IOG54pS0Xwmc8hw5_L07-Cja3_")
        url = "https://api.search.brave.com/res/v1/images/search"
        headers = {
            "x-subscription-token": api_key,
            'accept': 'application/json',
            'Cache-Control': 'no-cache',
            'Accept-Encoding': 'gzip'
        }

        params = {
            'q': query_text,
            'safesearch': 'off',
        }
        page = request.GET.get('page')
        if page:
            params['offset'] = (int(page) - 1) * 10

        response = requests.get(url, params=params, headers=headers)
        try:
            data = response.json()
        except Exception as e:
            return JsonResponse({"error": "Invalid JSON response from Brave API", "details": str(e)}, status=500)
            
        # Brave Image API structure is usually {"images": {"results": [...]}}
        results = data.get('images', {}).get('results', [])
        if not results and 'results' in data:
            results = data.get('results', [])

        for item in results:
            try:
                WebsiteImage.objects.get_or_create(
                    url=item.get('url'),
                    defaults={
                        'title': item.get('title'),
                        'description': item.get('description'),
                        'page_url': item.get('page_url'),
                        'thumbnail': item.get('thumbnail'),
                        'height': str(item.get('height', '')),
                        'width': str(item.get('width', '')),
                    }
                )
            except Exception:
                pass

        return JsonResponse(results, safe=False)


class AllWebsitesView(View):
    def get(self, request, *args, **kwargs):
        websites = Website.objects.all().order_by('-created_at')
        data = [
            {
                'url': w.url,
                'title': w.title,
                'body': w.body,
                'favicon': w.favicon,
                'query': w.query,
                'created_at': w.created_at,
            }
            for w in websites
        ]
        return JsonResponse({'results': data})


class SearchWebsitesView(View):
    def get(self, request, *args, **kwargs):
        q = request.GET.get('q', '')
        websites = Website.objects.filter(title__icontains=q) | Website.objects.filter(body__icontains=q)
        websites = websites.distinct().order_by('-created_at')
        data = [
            {
                'url': w.url,
                'title': w.title,
                'body': w.body,
                'favicon': w.favicon,
                'query': w.query,
                'created_at': w.created_at,
            }
            for w in websites
        ]
        return JsonResponse({'results': data})


class GoogleCustomSearchImageView(View):
    def get(self, request, *args, **kwargs):
        query_text = request.GET.get('q')
        API_KEY = os.getenv("GOOGLE_CUSTOM_SEARCH_KEY", "AIzaSyDmozzxUMPfhu1Tg0yNbAGpuV-ooqpUX0Y")
        SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "a6c0b28d85a34430d")

        url = 'https://www.googleapis.com/customsearch/v1'
        params = {
            'q': query_text,
            'key': API_KEY,
            'cx': SEARCH_ENGINE_ID,
            'searchType': 'image',
        }

        response = requests.get(url, params=params)
        results = response.json()
        return JsonResponse({'items': results.get('items', [])})
