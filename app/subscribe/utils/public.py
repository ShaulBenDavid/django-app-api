import jwt

from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed


def generate_temp_group_url(
    path: str, group_id: int, user_list_id: int, expires_in_days: int = 1
) -> str:
    """
    Generates a JWT for a temporary URL.

    :param user_list_id:
    :param group_id:
    :param path: The resource path or URL you want to secure.
    :param expires_in_days: The validity period for the temporary URL.
    :return: A signed JWT token.
    """
    expiration = datetime.utcnow() + timedelta(days=expires_in_days)

    payload = {
        "group_id": group_id,
        "user_list_id": user_list_id,
        "exp": expiration,
    }

    token = jwt.encode(payload, settings.SHARE_LINK_SECRET_KEY, algorithm="HS256")
    return f"{path}?token={token}"


def validate_temp_group_url(token: str) -> int:
    """
    Validates the JWT from a temporary URL.

    :param token: The JWT token from the URL.
    :return: The original path if the token is valid.
    :raises: AuthenticationFailed if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token, settings.SHARE_LINK_SECRET_KEY, algorithms=["HS256"]
        )

        group_id = payload["group_id"]
        user_list_id = payload["user_list_id"]
        expiration = payload["exp"]
        return int(group_id), int(user_list_id), int(expiration)
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationFailed("Invalid token")
