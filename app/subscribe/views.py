from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from core.models import Subscription, UserSubscriptionCollection
from .utils import get_youtube_subscriptions, transform_subscriptions


class SubscriptionsView(APIView):
    """
    SubscriptionsView - handle user subscribers.
    * Requires token authentication.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="X-Google-Token",
                type=OpenApiTypes.STR,
                description="Google token",
                required=True,
            )
        ],
        responses={200: {"subscriptions_count": OpenApiTypes.INT}},
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
            user_subscription_list, created = (
                UserSubscriptionCollection.objects.update_or_create(
                    user=request.user.profile,
                    defaults={"last_data_sync": timezone.now()},
                )
            )

            current_month = timezone.now().month
            last_sync_month = user_subscription_list.last_data_sync.month
            # We sync data from YouTube only once a month
            if current_month == last_sync_month and not created:
                subscriptions_count = user_subscription_list.subscriptions.count()
                return Response(
                    {
                        "subscriptions_count": subscriptions_count,
                        "last_sync_date": user_subscription_list.last_data_sync,
                    }
                )

            subscriptions = get_youtube_subscriptions(google_token)
            transformed_subscriptions = transform_subscriptions(subscriptions)

            # If Subscription not already exist in user list we will create and save
            for subscription_data in transformed_subscriptions:
                existing_subscriptions = user_subscription_list.subscriptions.filter(
                    channel_id=subscription_data["channel_id"]
                )

                if not existing_subscriptions.exists():
                    subscription, _ = Subscription.objects.get_or_create(
                        channel_id=subscription_data["channel_id"],
                        defaults={
                            "title": subscription_data["title"],
                            "description": subscription_data["description"],
                            "image_url": subscription_data["image_url"],
                        },
                    )
                    user_subscription_list.subscriptions.add(subscription)

            subscriptions_count = user_subscription_list.subscriptions.count()

            return Response(
                {
                    "subscriptions_count": subscriptions_count,
                    "last_sync_date": user_subscription_list.last_data_sync,
                }
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
