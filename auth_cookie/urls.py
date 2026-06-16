from django.urls import path
# from auth_cookie.apis import (
#     # LoginApi,
#     GoogleLoginApi,
#     TwitchLoginApi,
#     # SpotifyLoginApi,
#     # LogoutApi
#     # GoogleTestApi,
#     spotify_callback
# )
from auth_cookie.views_no_drf import google_login_api, vk_login_api

# from users.urls import CurrentUserViewAPI
from django.urls import path


urlpatterns = [
    # GOOGLE OAUTH
    # path('google/', redirect_to_google_oauth_url.as_view() ),
    # path('user', CurrentUserViewAPI.as_view() ),
    # path('google/callback', GoogleLoginApi.as_view() ),
    path('google/token/', google_login_api, name='google_login_api'),
    path('google/token', google_login_api),

    # VK OAUTH
    path('vk/token/', vk_login_api, name='vk_login_api'),
    path('vk/token', vk_login_api),

    # path('google/callback', GoogleTestApi.as_view() ),
    # path('google/callback', spotify_callback ),
    # path('google/', GoogleTestApi.as_view() ),

    # SPOTIFY OAUTH
    # path('spotify/', redirect_to_spotify_oauth_url.as_view() ),
    # path('spotify/callback', SpotifyLoginApi),
    # path('spotify/token', SpotifyLoginApi),

    # APPLE OAUTH
    # path('apple/', redirect_to_apple_oauth_url.as_view() ),
    # path('apple/callback', apple_callback.as_view() ),
    # path('apple/token', apple_callback.as_view() ),

    # CSRF OAUTH PROVIDERS
    # path("apple/authorize", csrf_exempt(AppleAuthorizeView.as_view()), name="apple-authorize"),
    # path("apple/callback", csrf_exempt(AppleCallbackView.as_view()), ame="apple-callback",),
    # path("google/authorize", csrf_exempt(GoogleAuthorizeView.as_view()), name="google-authorize"),
    # path("google/callback", csrf_exempt(GoogleCallbackView.as_view()), name="google-callback",),


    # django react tutorial youtube TECHWITHTIM
    # path('spotify/authorize', AuthURL.as_view()),
    # path('spotify/callback', spotify_callback), #alternative
    # path('spotify/is-authenticated', IsAuthenticated.as_view()),


]
