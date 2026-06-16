from django.urls import path


from users.views.signin_signup_no_drf import signup_view, signin_view
from users.views import (
    google_token_exchange_view,
    userlist,
    user_detail_api,
    user_username_detail_api,
    user_username_posts_api,
    user_username_watchlist_api,
    user_username_tracks_api,
    user_username_photos_api,
    user_username_albums_api,
    user_username_videos_api,
    forgot_password_api,
    password_reset_confirm_api,
    user_search_api
)
from users.views.current_user import user_me_view
from users.views.avatar_upload_no_drf import upload_avatar_view

from movies.views import (get_watchlist, user_watchlist_api)

urlpatterns = [

    path('signup/', signup_view, name='signup'),
    path('signin/', signin_view, name='signin'),
    path('me/', user_me_view, name='user_me'),
    path('me/avatar/', upload_avatar_view, name='upload_avatar'),

    path('callback/', signin_view, name='signin_callback'),
    path('token/', google_token_exchange_view, name='google_token_exchange'),
    path('token', google_token_exchange_view, name='google_token_exchange'),

    path('list/', userlist, name='userlist'),
    path('search/', user_search_api, name='user_search'),
    path('<int:user_id>/', user_detail_api, name='user_detail'),
    path('<int:user_id>/watchlist/', user_watchlist_api, name='user_watchlist'),
    
    path('<str:username>/', user_username_detail_api, name='user_username_detail'),
    path('<str:username>/posts/', user_username_posts_api, name='user_username_posts'),
    path('<str:username>/photos/', user_username_photos_api, name='user_username_photos'),
    path('<str:username>/albums/', user_username_albums_api, name='user_username_albums'),
    path('<str:username>/videos/', user_username_videos_api, name='user_username_videos'),
    path('<str:username>/tracks/', user_username_tracks_api, name='user_username_tracks'),
    path('<str:username>/watchlist/', user_username_watchlist_api, name='user_username_watchlist'),

    path('password-reset/', forgot_password_api, name='forgot_password'),
    path('password-reset-confirm/<str:uidb64>/<str:token>/', password_reset_confirm_api, name='password_reset_confirm'),


]
