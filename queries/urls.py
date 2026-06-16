from django.urls import path
from queries.views_no_drf import (
    bing_query_view,
    brave_query_view,
    brave_images_search_view,
    google_firefox_query_view,
    google_query_view,
)
from queries.views_v2 import (
    GoogleQueryListView,
    GoogleQuerySearchView,
    GoogleQueryAllSearchView,
)


urlpatterns = [

    path('bing/search', bing_query_view, name="search"),

    path('brave/search', brave_query_view, name="search"),
    path('brave/images/search', brave_images_search_view, name="search"),

    path('google/firefox/search', google_firefox_query_view, name="search"),
    path('google/search-old', google_query_view, name="search"),

    path('google/all', GoogleQueryListView.as_view(), name='google_all'),
    path('google/all/search', GoogleQueryAllSearchView.as_view(), name='google_all_search'),
    path('google/search', GoogleQuerySearchView.as_view(), name='google_search_v2'),

]
