import requests
from typing import Dict, Any, Tuple
from django.conf import settings
from django.core.exceptions import ValidationError
from user.serializers import CustomTokenObtainPairSerializer

GOOGLE_ID_TOKEN_INFO_URL = "https://www.googleapis.com/oauth2/v3/tokeninfo"
GOOGLE_ACCESS_TOKEN_OBTAIN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def generate_tokens_for_user(user):
    """
    Generate access and refresh tokens for the given user
    """
    serializer = CustomTokenObtainPairSerializer()
    token_data = serializer.get_token(user)
    access_token = token_data.access_token
    refresh_token = token_data
    return access_token, refresh_token


def google_get_tokens(*, code: str, redirect_uri: str) -> Tuple[str, str]:
    data = {
        "code": code,
        "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
        "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        "redirect_uri": redirect_uri,
        "access_type": "offline",
        "grant_type": "authorization_code",
    }

    try:
        response = requests.post(GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data)

        if not response.ok:
            raise ValidationError(response.json())

        access_token = response.json()["access_token"]
        refresh_token = response.json()["refresh_token"]

        return access_token, refresh_token

    except requests.exceptions.RequestException as e:
        # Handle requests-related errors
        raise ValidationError(f"Error during token exchange: {str(e)}")
    except Exception as e:
        # Handle other unexpected errors
        raise ValidationError(f"Unexpected error: {str(e)}")

def google_refresh_access_token(refresh_token: str) -> str:
    data = {
        "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
        "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }

    response = requests.post(GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data)

    if not response.ok:
        raise ValidationError(
            "Failed to obtain access token from Google using refresh token."
        )

    access_token = response.json()["access_token"]
    return access_token


def google_get_user_info(*, access_token: str) -> Dict[str, Any]:
    response = requests.get(GOOGLE_USER_INFO_URL, params={"access_token": access_token})

    if not response.ok:
        raise ValidationError("Failed to obtain user info from Google.")

    return response.json()


def get_first_matching_attr(obj, *attrs, default=None):
    for attr in attrs:
        if hasattr(obj, attr):
            return getattr(obj, attr)

    return default


def get_error_message(exc) -> str:
    if hasattr(exc, "message_dict"):
        return exc.message_dict
    error_msg = get_first_matching_attr(exc, "message", "messages")

    if isinstance(error_msg, list):
        error_msg = ", ".join(error_msg)

    if error_msg is None:
        error_msg = str(exc)

    return error_msg
