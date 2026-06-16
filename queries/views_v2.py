import requests
from django.db import models
from django.http import JsonResponse
from django.views import View
from queries.models import GoogleQuery


class GoogleQueryListView(View):
    def get(self, request, *args, **kwargs):
        queries = GoogleQuery.objects.all().order_by('-created_at')
        data = [
            {
                'query_text': q.query_text,
                'suggestion': q.suggestion,
                'created_at': q.created_at,
            }
            for q in queries
        ]
        return JsonResponse({'results': data})


class GoogleQuerySearchView(View):
    def get(self, request, *args, **kwargs):
        query_text = request.GET.get('q')
        if not query_text:
            return JsonResponse({'error': 'Missing query parameter `q`'}, status=400)

        url = "https://www.google.com/complete/search"
        params = {
            'client': 'chrome',
            'q': query_text,
            'hl': 'en-US',
            'dpr': '1.5',
        }

        response = requests.get(url, params=params)
        data = response.json()
        suggestions = data[1]

        for item in suggestions:
            GoogleQuery.objects.get_or_create(
                query_text=query_text,
                suggestion=item,
            )

        output = {
            "results": [{"query": item} for item in suggestions]
        }
        return JsonResponse(output)


class GoogleQueryAllSearchView(View):
    def get(self, request, *args, **kwargs):
        q = request.GET.get('q', '')
        if not q:
            return JsonResponse({'error': 'Missing query parameter `q`'}, status=400)

        queries = GoogleQuery.objects.filter(
            models.Q(query_text__icontains=q) | models.Q(suggestion__icontains=q)
        ).distinct().order_by('-created_at')

        data = [
            {
                'query_text': qr.query_text,
                'suggestion': qr.suggestion,
                'created_at': qr.created_at,
            }
            for qr in queries
        ]
        return JsonResponse({'results': data})
