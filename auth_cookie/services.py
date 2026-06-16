import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
import jwt
import datetime

from users.models import User
from users.services import user_record_login


GOOGLE_ID_TOKEN_INFO_URL = 'https://www.googleapis.com/oauth2/v3/tokeninfo'
GOOGLE_ACCESS_TOKEN_OBTAIN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'


google_client_id = settings.GOOGLE_CLIENT_ID
google_client_secret = settings.GOOGLE_CLIENT_SECRET

def set_jwt_access_cookie(name, access_token, response):
    cookie_name = getattr(settings, 'JWT_AUTH_COOKIE', 'access_token')
    # Use a default 1 day expiration if not configured
    access_token_expiration = timezone.now() + datetime.timedelta(days=1)
    cookie_secure = getattr(settings, 'JWT_AUTH_SECURE', False)
    cookie_httponly = getattr(settings, 'JWT_AUTH_HTTPONLY', True)
    cookie_samesite = getattr(settings, 'JWT_AUTH_SAMESITE', 'Lax')

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
    from users.token_utils import generate_tokens_for_user
    tokens = generate_tokens_for_user(user)
    token = tokens['access']

    set_jwt_access_cookie('access_token', token, response)

    user_record_login(user=user)
    if isinstance(response, str):
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
        raise ValidationError(f'Failed to obtain access token from Google: {response.text}')

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


def vk_get_access_token(*, code, redirect_uri):
    data = {
        'client_id': vk_client_id,
        'client_secret': vk_client_secret,
        'redirect_uri': redirect_uri,
        'code': code
    }

    response = requests.get(VK_ACCESS_TOKEN_URL, params=data)

    if not response.ok:
        raise ValidationError(f'Failed to obtain access token from VK: {response.text}')

    return response.json()


def vk_get_user_info(*, access_token, user_id):
    params = {
        'user_ids': user_id,
        'fields': 'photo_max,email',
        'access_token': access_token,
        'v': '5.131'
    }

    response = requests.get(VK_USER_INFO_URL, params=params)

    if not response.ok:
        raise ValidationError('Failed to obtain user info from VK.')

    data = response.json()
    if 'error' in data:
        raise ValidationError(f"VK API Error: {data['error']['error_msg']}")

    return data['response'][0]



#
