import requests
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

# Create your views here.
# class WebsiteCreateView(generics.CreateAPIView):
class BingQueryView(APIView):
    # serializer_class = WebsiteSerializer

    def get(self, request, *args, **kwargs):
        # query_text = request.data.get('q', '')
        query_text = self.request.query_params.get('q', None)
        # scrape_and_save_autosuggest.delay(query_text)  # Trigger the Celery task asynchronously


        api_key = "23c6c54ede484f7c9586245ad7a0fb18"
        url = f"https://api.bing.microsoft.com/v7.0/suggestions?q={query_text}"
        headers = {
            "Ocp-Apim-Subscription-Key": api_key
        }


        response = requests.get(url, headers=headers)
        data = response.json()

        # return Response({'message': 'Scraping initiated. Results will be saved shortly.'})
        return Response(data)

class BraveQueryView(APIView):
    # serializer_class = WebsiteSerializer

    def get(self, request, *args, **kwargs):
        # query_text = request.data.get('q', '')
        # query_text = self.request.query_params.get('q', None)
        query_text = request.GET.get('q')
        # scrape_and_save_autosuggest.delay(query_text)  # Trigger the Celery task asynchronously
        api_key = "BSA98IuMyCoiHdPaE05qvoJGk02tod-"
        url = f"https://api.search.brave.com/res/v1/suggest/search?count=20"
        headers = {
            "x-subscription-token": api_key,
            'accept': 'application/json',
            'Cache-Control': 'no-cache'
        }

        response = requests.get(url, params={'q': query_text}, headers=headers)

        data = response.json()

        # return Response({'message': 'Scraping initiated. Results will be saved shortly.'})
        # return HttpResponse(data)
        # return Response(data)
        return JsonResponse({
            'word': query_text,
            'results': data['results']

        })


class BraveImagesSearchView(APIView):
    # serializer_class = WebsiteSerializer

    def get(self, request, *args, **kwargs):
        # query_text = request.data.get('q', '')
        # query_text = self.request.query_params.get('q', None)
        query_text = request.GET.get('q')
        # scrape_and_save_autosuggest.delay(query_text)  # Trigger the Celery task asynchronously
        api_key = "BSA98IuMyCoiHdPaE05qvoJGk02tod-"
        url = f"https://api.search.brave.com/res/v1/images/search?count=100"
        headers = {
            "x-subscription-token": api_key,
            'accept': 'application/json',
            'Cache-Control': 'no-cache'
        }
        params = {
            'q': query_text,
            'count': '100',
        }
        response = requests.get(url, params=params, headers=headers)

        data = response.json()

        # return Response({'message': 'Scraping initiated. Results will be saved shortly.'})
        # return HttpResponse(data)
        # return Response(data)
        return JsonResponse({
            'word': query_text,
            'results': data['results']

        })


class GoogleFirefoxQueryView(APIView):
    # serializer_class = WebsiteSerializer

    def get(self, request, *args, **kwargs):
        # query_text = self.request.query_params.get('q', None)
        query_text = request.GET.get('q')

        # if (query_text.contains == "site:"):
        #     req.bing()

        cursor_position = request.GET.get('cp')
        # scrape_and_save_autosuggest.delay(query_text)  # Trigger the Celery task asynchronously
        api_key = "BSA98IuMyCoiHdPaE05qvoJGk02tod-"
        url = f"https://www.google.com/complete/search"
        # url = f"https://suggestqueries-clients6.youtube.com/complete/search"
        # headers = {
        #     "x-subscription-token": api_key,
        #     'accept': 'application/json',
        #     'Cache-Control': 'no-cache'
        # }
        params = {
            # 'client': 'gws-wiz',
            # 'client': 'gws-wiz-serp',
            'client': 'firefox',
            # 'client': 'youtube',
            # 'client': 'chrome',
            'q': query_text,
            # 'cp': cursor_position,
            # 'pq': query_text,
            'hl': 'en-US',

            'dpr': '1.5',

        }
        response = requests.get(url, params=params, )
        data = response.json()
        # return Response(data)
        # return Response({'message': 'Scraping initiated. Results will be saved shortly.'})
        # return HttpResponse(data)

        output = {
            "results": [{"query": item} for item in data[1]]
        }

        # create_query_name.delay()
        # Query.objects.create(name=item)
        # print(output)
        return Response(output)


class GoogleQueryView(APIView):
    # serializer_class = WebsiteSerializer

    def get(self, request, *args, **kwargs):
        # query_text = self.request.query_params.get('q', None)
        query_text = request.GET.get('q')
        cursor_position = request.GET.get('cp')
        # scrape_and_save_autosuggest.delay(query_text)  # Trigger the Celery task asynchronously
        api_key = "BSA98IuMyCoiHdPaE05qvoJGk02tod-"
        url = f"https://www.google.com/complete/search"
        # headers = {
        #     "x-subscription-token": api_key,
        #     'accept': 'application/json',
        #     'Cache-Control': 'no-cache'
        # }
        params = {
            # 'client': 'gws-wiz',
            # 'client': 'gws-wiz-serp',
            'client': 'chrome',
            'q': query_text,
            # 'cp': cursor_position,
            # 'pq': query_text,
            'hl': 'en-US',
            'dpr': '1.5',

        }
        response = requests.get(url, params=params, )
        data = response.json()
        # return Response(data)
        # return Response({'message': 'Scraping initiated. Results will be saved shortly.'})
        # return HttpResponse(data)

        output = {
            "results": [{"query": item} for item in data[1]]
        }

        # print(output)
        return Response(output)
