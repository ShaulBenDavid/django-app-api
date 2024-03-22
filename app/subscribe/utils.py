import requests
from django.conf import settings

# Define YouTube Data API endpoint
YOUTUBE_SUBSCRIPTIONS_URL = "https://www.googleapis.com/youtube/v3/subscriptions"


def get_youtube_subscriptions(access_token):
    params = {
        "part": "snippet,contentDetails",
        "mine": "true",
        "key": "AIzaSyBOOry61odkj5jCl1TbDny-zPmYce0ShPg",
        "maxResults": 200,  # Adjust as needed
        "access_token": access_token,
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
