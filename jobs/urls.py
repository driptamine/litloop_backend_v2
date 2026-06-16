from django.urls import path
from jobs.views_application import ApplicationView
from jobs.views import vacancies_api
urlpatterns = [
    path('api/applications/', ApplicationView.as_view(), name='application_create'),
    path('api/vacancies/', vacancies_api, name='vacancies_api'),
]
