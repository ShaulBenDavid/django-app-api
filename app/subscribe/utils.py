import requests
from django.conf import settings

YOUTUBE_SUBSCRIPTIONS_URL = "https://www.googleapis.com/youtube/v3/subscriptions"


def get_youtube_subscriptions(access_token):
    subscriptions = []
    page_token = None

    while True:
        params = {
            "part": "snippet,contentDetails",
            "mine": True,
            "key": settings.GOOGLE_API_KEY,
            "maxResults": 50,
            "pageToken": page_token
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


def transform_subscriptions(subscriptions):
    """
    Transform the subscriptions data as needed.
    """
    transformed_subscriptions = []
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
    return transformed_subscriptions
