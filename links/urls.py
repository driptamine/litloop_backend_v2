from django.urls import path

from links.views import (
    all_links_api,
    save_link,
    search_by_tag,
    upload_csv_api,
    upload_csv_bulk 
)


urlpatterns = [
    path('save/', save_link, name="save_link"),
    path('search/',  search_by_tag, name='search_links_api'),
    path('all/', all_links_api, name='all_links_api'),
    path('upload-csv/', upload_csv_api, name='upload_csv_api'),
    path('upload-csv-bulk/', upload_csv_bulk, name='upload_csv_api'),
]
