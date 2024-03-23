import requests
from django.conf import settings

# Define YouTube Data API endpoint
YOUTUBE_SUBSCRIPTIONS_URL = "https://www.googleapis.com/youtube/v3/subscriptions"


def get_youtube_subscriptions(access_token):
    params = {
        "part": "snippet,contentDetails",
        "mine": True,
        "key": settings.GOOGLE_API_KEY,
        "maxResults": 200,  # Adjust as needed
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(
            YOUTUBE_SUBSCRIPTIONS_URL, params=params, headers=headers
        )
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        data = response.json()
        subscriptions = data.get("items", [])
        return subscriptions
    except requests.exceptions.RequestException as e:
        # Log the error or handle it as needed
        raise RuntimeError(f"Failed to retrieve subscriptions: {e}")


def transform_subscriptions(subscriptions):
    """
    Transform the subscriptions data as needed.
    """
    transformed_subscriptions = []
    for subscription in subscriptions:
        snippet = subscription.get("snippet", {})

        title = snippet.get("title", "")
        channel_id = snippet.get("channelId", "")
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
