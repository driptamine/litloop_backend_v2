# from __future__ import absolute_import
from django.urls import path
from websites.views_v2 import (
    BingWebsiteSearchView,
    BingImageSearchView,
    BraveWebsiteSearchView,
    BraveImageSearchView,
    GoogleCustomSearchImageView
)

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

    path('brave/search', BraveWebsiteSearchView.as_view(), name="search"),
    path('brave/images/search', BraveImageSearchView.as_view(), name="search"),

    path('google/custom/search', GoogleCustomSearchImageView.as_view(), name='search' ),


    # path('url/', ModifyHTMLView.as_view(), name='modify_html'),

    # localhost:8000/websites/modify?url=https://www.google.com
]
