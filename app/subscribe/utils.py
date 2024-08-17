import requests
import jwt

from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed

YOUTUBE_SUBSCRIPTIONS_URL = "https://www.googleapis.com/youtube/v3/subscriptions"
YOUTUBE_CHANNELS_URL = "https://www.googleapis.com/youtube/v3/channels"
YOUTUBE_PLAYLIST_URL = "https://www.googleapis.com/youtube/v3/playlistItems"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"


def get_youtube_subscriptions(access_token):
    subscriptions = []
    page_token = None

    while True:
        params = {
            "part": "snippet,contentDetails",
            "mine": True,
            "key": settings.GOOGLE_API_KEY,
            "maxResults": 50,
            "pageToken": page_token,
        }
        headers = {"Authorization": f"Bearer {access_token}"}

        try:
            response = requests.get(
                YOUTUBE_SUBSCRIPTIONS_URL, params=params, headers=headers
            )
            response.raise_for_status()
            data = response.json()
            subscriptions.extend(data.get("items", []))
            page_token = data.get("nextPageToken")
            if not page_token:
                break  # Exit the loop if there are no more pages
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to retrieve subscriptions: {e}")

    return subscriptions


def get_upload_playlist_ids(access_token, channel_ids):
    playlist_ids = []
    for i in range(0, len(channel_ids), 50):
        params = {
            "part": "contentDetails",
            "key": settings.GOOGLE_API_KEY,
            "id": [],
        }
        headers = {"Authorization": f"Bearer {access_token}"}
        chunk = channel_ids[i : i + 50]
        params["id"] = ",".join(chunk)
        try:
            response = requests.get(
                url=YOUTUBE_CHANNELS_URL, params=params, headers=headers
            )
            response.raise_for_status()
            channel_response = response.json()

            for item in channel_response["items"]:
                uploads_playlist_id = item["contentDetails"]["relatedPlaylists"][
                    "uploads"
                ]
                playlist_ids.append(uploads_playlist_id)
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to retrieve playlist_ids: {e}")

    return playlist_ids


def get_latest_uploads(access_token, playlist_ids):
    latest_videos = []
    for i in range(0, len(playlist_ids), 50):  # Process in batches of 50
        chunk = playlist_ids[i : i + 50]
        for playlist_id in chunk:
            try:
                params = {
                    "part": "snippet",
                    "key": settings.GOOGLE_API_KEY,
                    "maxResults": 1,
                    "playlistId": playlist_id,
                }
                headers = {"Authorization": f"Bearer {access_token}"}
                response = requests.get(
                    url=YOUTUBE_PLAYLIST_URL, params=params, headers=headers
                )
                response.raise_for_status()
                playlist_response = response.json()
                if playlist_response["items"]:
                    latest_videos.append(
                        playlist_response["items"][0]["snippet"]["resourceId"][
                            "videoId"
                        ]
                    )
            except requests.exceptions.RequestException as e:
                raise RuntimeError(f"Failed to retrieve get_latest_uploads: {e}")
    return latest_videos


def get_video_details(access_token, video_ids):
    video_details = []
    for i in range(0, len(video_ids), 50):  # Process in batches of 50
        params = {
            "part": "snippet",
            "key": settings.GOOGLE_API_KEY,
            "id": ",".join(video_ids[i : i + 50]),
        }
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            response = requests.get(
                url=YOUTUBE_VIDEOS_URL, params=params, headers=headers
            )
            response.raise_for_status()
            video_response = response.json()
            video_details.extend(video_response["items"])
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to retrieve video details: {e}")
    return video_details


def transform_subscriptions(subscriptions):
    """
    Transform the subscriptions data as needed.
    """
    transformed_subscriptions = []
    channel_ids = []
    for subscription in subscriptions:
        snippet = subscription.get("snippet", {})

        title = snippet.get("title", "")
        channel_id = snippet.get("resourceId", {}).get("channelId", "")
        image_url = snippet.get("thumbnails", {}).get("medium", {}).get("url", "")
        description = snippet.get("description", "")

        transformed_subscriptions.append(
            {
                "title": title,
                "channel_id": channel_id,
                "image_url": image_url,
                "description": description,
            }
        )
        channel_ids.append(channel_id)
    return transformed_subscriptions, channel_ids


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
