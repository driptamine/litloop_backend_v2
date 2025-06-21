import requests, os
from typing import Dict, Any

from django.conf import settings
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.utils import timezone

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings as jwt_settings


from users.models import User
from users.services import user_record_login


GOOGLE_ID_TOKEN_INFO_URL = 'https://www.googleapis.com/oauth2/v3/tokeninfo'
GOOGLE_ACCESS_TOKEN_OBTAIN_URL = 'https://oauth2.googleapis.com/token'
# GOOGLE_ACCESS_TOKEN_OBTAIN_URL = 'https://accounts.google.com/o/oauth2/token'
GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'
TWITCH_USER_INFO_URL = 'https://api.twitch.com/users'


SPOTIFY_CLIENT_ID = "c57cfe40c3a640449c4766ee61ec9d59"
SPOTIFY_CLIENT_SECRET = "8c5ae0b0d9df47c8bae2804fe8e03cfa"


TWITCH_CLIENT_ID = os.environ.get("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.environ.get("TWITCH_CLIENT_SECRET")


google_client_id = os.environ.get("GOOGLE_CLIENT_ID")
google_client_secret = os.environ.get("GOOGLE_SECRET_KEY")

# reference https://github.com/iMerica/dj-rest-auth/blob/ea140563c47ba4289fab41586add6a40b1733c8c/dj_rest_auth/jwt_auth.py#L9
def set_jwt_access_cookie(name, access_token, response):
    cookie_name = getattr(settings, 'JWT_AUTH_COOKIE', None)
    access_token_expiration = (timezone.now() + jwt_settings.ACCESS_TOKEN_LIFETIME)
    cookie_secure = getattr(settings, 'JWT_AUTH_SECURE', False)
    cookie_httponly = getattr(settings, 'JWT_AUTH_HTTPONLY', True)
    cookie_samesite = getattr(settings, 'JWT_AUTH_SAMESITE', 'Lax')

    if cookie_name:
        response.set_cookie(
            key      = cookie_name,
            value    = access_token,
            expires  = access_token_expiration,
            secure   = cookie_secure,
            httponly = cookie_httponly,
            samesite = cookie_samesite,
        )
        return response


def jwt_login(*, response, user):

    # 1st version own JWT generation
    refresh_token = RefreshToken.for_user(user)
    # token = str(refresh_token.access_token)
    token = refresh_token.access_token

    # if api_settings.JWT_AUTH_COOKIE:
        # Reference: https://github.com/Styria-Digital/django-rest-framework-jwt/blob/master/src/rest_framework_jwt/compat.py#L43

    set_jwt_access_cookie('access_token', token, response)

    user_record_login(user=user)
    response = response + "?cookie=%s" % token
    return response
    # return HttpResponseRedirect(response+"?token="+token)


def google_validate_id_token(*, id_token):
    # Reference: https://developers.google.com/identity/sign-in/web/backend-auth#verify-the-integrity-of-the-id-token
    response = requests.get(
        GOOGLE_ID_TOKEN_INFO_URL,
        params={'id_token': id_token}
    )

    if not response.ok:
        raise ValidationError('id_token is invalid.')

    audience = response.json()['aud']

    if audience != settings.GOOGLE_OAUTH2_CLIENT_ID:
        raise ValidationError('Invalid audience.')

    return True




def google_get_access_token(*, code, redirect_uri):
    # Reference: https://developers.google.com/identity/protocols/oauth2/web-server#obtainingaccesstokens
    data = {
        'code': code,
        'client_id': google_client_id,
        'client_secret': google_client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }

    response = requests.post("https://oauth2.googleapis.com/token", data=data)
    # response = requests.post("https://accounts.google.com/o/oauth2/token", data=data)

    if not response.ok:
        raise ValidationError('Failed to obtain access token from Google.')

    # access_token = response.json()['access_token']
    # return access_token

    response = response.json()
    return response



def google_get_user_info(*, access_token):
    # Reference: https://developers.google.com/identity/protocols/oauth2/web-server#callinganapi
    response = requests.get(
        GOOGLE_USER_INFO_URL,
        params={'access_token': access_token}
    )

    if not response.ok:
        raise ValidationError('Failed to obtain user info from Google.')

    return response.json()

def twitch_get_user_info(*, access_token):
    # Reference: https://developers.google.com/identity/protocols/oauth2/web-server#callinganapi
    response = requests.get(
        TWITCH_USER_INFO_URL,
        params={'access_token': access_token}
    )

    if not response.ok:
        raise ValidationError('Failed to obtain user info from Google.')

    return response.json()


def spotify_get_access_token(*, code: str, redirect_uri: str) -> str:
    # Reference: https://developers.google.com/identity/protocols/oauth2/web-server#obtainingaccesstokens
    data = {
        'code': code,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET,
        'redirect_uri': redirect_uri,
        'grant_type': 'client_credentials'
    }

    auth_client = SPOTIFY_CLIENT_ID + SPOTIFY_CLIENT_SECRET
    auth_encode = 'Basic ' + base64.b64encode(auth_client.encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_encode}"
    }
    response = requests.post("https://accounts.spotify.com/api/token", data=data, headers=headers)

    if not response.ok:
        raise ValidationError('Failed to obtain access token from Google.')

    access_token = response.json()['access_token']

    return access_token


def twitch_get_access_token(*, code: str, redirect_uri: str) -> str:
    # Reference: https://developers.google.com/identity/protocols/oauth2/web-server#obtainingaccesstokens
    data = {
        'code': code,
        'client_id': TWITCH_CLIENT_ID,
        'client_secret': TWITCH_CLIENT_SECRET,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }


    response = requests.post("https://id.twitch.tv/oauth2/token", data=data)
    response = response.json()
    # if not response.ok:
    #     raise ValidationError('Failed to obtain access token from Google.')



    return response
    # return response


def spotify_get_user_info(*, access_token: str) -> Dict[str, Any]:
    # Reference: https://developers.google.com/identity/protocols/oauth2/web-server#callinganapi

    header = {
        "Authorization": "Bearer" + access_token
    }

    response = requests.get(
        "https://api.spotify.com/v1/me",
        headers=header
    )

    if not response.ok:
        raise ValidationError('Failed to obtain user info from Google.')

    return response.json()



#
