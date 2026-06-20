import os
import requests
from django.http import JsonResponse
from django.views import View
from websites.models import Website
from queries.models import Query


class ScrapeBraveWebsitesView(View):
    def _get_query_text(self, request):
        if request.method == 'GET':
            return request.GET.get('q', '').strip()
        return request.POST.get('q', '').strip()

    def _get_cached_results(self, query_text):
        query_obj = Query.objects.filter(query_text=query_text, is_crawled=True).first()
        if not query_obj:
            return None
        websites = Website.objects.filter(query=query_text).order_by('-created_at')
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
        return {'query_text': query_text, 'is_crawled': True, 'cached': True, 'results': data}

    def _scrape_from_brave(self, query_text):
        query_obj, _ = Query.objects.get_or_create(query_text=query_text)

        api_key = os.getenv("BRAVE_API_KEY", "BSA-7IOG54pS0Xwmc8hw5_L07-Cja3_")
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "x-subscription-token": api_key,
            'accept': 'application/json',
            'Cache-Control': 'no-cache',
            'Accept-Encoding': 'gzip'
        }
        params = {'q': query_text}

        response = requests.get(url, params=params, headers=headers)
        if response.status_code != 200:
            return JsonResponse({"error": "Brave API request failed"}, status=502)

        data = response.json()
        results = data.get('web', {}).get('results', [])

        serp_results = []
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
            serp_results.append({
                'url': item.get('url'),
                'title': item.get('title'),
                'body': item.get('description'),
                'favicon': item.get('favicon'),
            })

        query_obj.is_crawled = True
        query_obj.save()

        return JsonResponse({'query_text': query_text, 'is_crawled': True, 'cached': False, 'results': serp_results})

    def get(self, request, *args, **kwargs):
        query_text = self._get_query_text(request)
        if not query_text:
            return JsonResponse({"error": "query_text is required"}, status=400)

        cached = self._get_cached_results(query_text)
        if cached:
            return JsonResponse(cached)

        return self._scrape_from_brave(query_text)

    def post(self, request, *args, **kwargs):
        query_text = self._get_query_text(request)
        if not query_text:
            return JsonResponse({"error": "query_text is required"}, status=400)

        cached = self._get_cached_results(query_text)
        if cached:
            return JsonResponse(cached)

        return self._scrape_from_brave(query_text)
