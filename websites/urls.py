# from __future__ import absolute_import
from django.urls import path
from websites.views_v2 import (
    BingWebsiteSearchView,
    BingImageSearchView,
    BraveImageSearchView,
    GoogleCustomSearchImageView,
    AllWebsitesView,
    SearchWebsitesView,
)
from websites.views_v3 import ScrapeBraveWebsitesView

# from websites.parser.inject_html import (
#     ModifyHTMLView
# )

# from websites.parser.inject_html_undetected import (
#     ModifyHTMLView
# )

# from websites.parser.inject_html_selenium import (
#     ModifyHTMLView
# )


urlpatterns = [
    # path('', TrackListAPIView.as_view(), name="posts"),

    path('bing/search', BingWebsiteSearchView.as_view(), name="search"),
    path('bing/images/search', BingImageSearchView.as_view(), name="search"),

    path('brave/search', ScrapeBraveWebsitesView.as_view(), name="search"),
    path('brave/images/search', BraveImageSearchView.as_view(), name="search"),

    path('google/custom/search', GoogleCustomSearchImageView.as_view(), name='search' ),

    path('all', AllWebsitesView.as_view(), name='all'),
    path('search', SearchWebsitesView.as_view(), name='search'),

    path('brave/scrape', ScrapeBraveWebsitesView.as_view(), name='brave_scrape'),

    # path('url/', ModifyHTMLView.as_view(), name='modify_html'),

    # localhost:8000/websites/modify?url=https://www.google.com
]
