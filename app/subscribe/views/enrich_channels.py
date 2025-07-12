from django.utils import timezone
from datetime import timedelta

from django.db.models import Prefetch, Q
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import UserSubscriptionCollection, Subscription, Upload

from subscribe.utils.subscriptions import (
    get_upload_playlist_ids,
    get_latest_uploads,
    get_video_details,
    transform_video_details,
)


class EnrichChannelsView(APIView):
    """
    EnrichChannelsView - handle user subscribers.
    * Requires token authentication.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "X-Google-Token",
                OpenApiTypes.STR,
                description="Google token",
                required=True,
                location=OpenApiParameter.HEADER,
            )
        ],
    )
    def get(self, request):
        """
        Return a list of all user subscriptions.
        """
        # Retrieve Google token from X-Google-Token header
        google_token = request.headers.get("X-Google-Token")
        if not google_token:
            return Response(
                {"error": "X-Google-Token header is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            one_week_ago = timezone.now() - timedelta(weeks=1)

            collection = UserSubscriptionCollection.objects.get(
                user=request.user.profile
            )
            channels_ids = (
                Subscription.objects.filter(
                    Q(upload__last_sync__lt=one_week_ago) | Q(upload__isnull=True),
                    users_list=collection,
                )
                .select_related("upload")
                .order_by("-upload__last_sync")
                .values_list("channel_id", "id")[:30]
            )

            ids_key_values = dict(channels_ids)

            subscriptions_playlist_ids = get_upload_playlist_ids(
                access_token=google_token, channel_ids=list(ids_key_values.keys())
            )
            latest_videos = get_latest_uploads(
                access_token=google_token, playlist_ids=subscriptions_playlist_ids
            )
            videos_detail = get_video_details(
                access_token=google_token, video_ids=latest_videos
            )

            transformed_videos = transform_video_details(videos_detail)

            for video in transformed_videos:
                subscription_id = ids_key_values.get(video["subscription"])

                if subscription_id:
                    Upload.objects.update_or_create(
                        subscription_id=subscription_id,
                        defaults={
                            "title": video["title"],
                            "upload_time": video["upload_time"],
                            "video_url": video["video_url"],
                            "video_image_url": video["video_image_url"],
                            "last_sync": timezone.now,
                        },
                    )

            return Response(
                {
                    "is_data_synced": True,
                }
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
