from datetime import timedelta
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status, generics
from core.models import Subscription, UserSubscriptionCollection
from core.utils.pagination import StandardResultsSetPagination
from subscribe.filters import SubscriptionFilter
from subscribe.serializers.subscriptions import DetailedSubscriptionSerializer

from subscribe.utils.subscriptions import (
    get_youtube_subscriptions,
    transform_subscriptions,
)


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
            user_subscription_list, created = (
                UserSubscriptionCollection.objects.update_or_create(
                    user=request.user.profile
                )
            )

            current_date = timezone.now()
            last_sync_date = user_subscription_list.last_data_sync or timezone.now()

            time_difference = current_date - last_sync_date

            # We sync data from YouTube only once a week
            if time_difference <= timedelta(days=7) and not created:
                subscriptions_count = user_subscription_list.subscriptions.count()
                return Response(
                    {
                        "subscriptions_count": subscriptions_count,
                        "last_sync_date": user_subscription_list.last_data_sync,
                        "is_data_synced": False,
                    }
                )

            subscriptions = get_youtube_subscriptions(access_token=google_token)
            transformed_subscriptions, _ = transform_subscriptions(
                subscriptions=subscriptions
            )

            existing_subscriptions = user_subscription_list.subscriptions.all()
            # remove subscription from user data
            subscriptions_to_remove = existing_subscriptions.exclude(
                channel_id__in=[sub["channel_id"] for sub in transformed_subscriptions]
            )
            user_subscription_list.subscriptions.remove(*subscriptions_to_remove)

            for subscription_to_remove in subscriptions_to_remove:
                group = subscription_to_remove.group.filter(
                    user_list=user_subscription_list
                ).first()
                if group:
                    group.subscriptions.remove(subscription_to_remove)

            # Sync the fetched subscriptions with the user's subscriptions
            for subscription_data in transformed_subscriptions:
                subscription, _ = Subscription.objects.update_or_create(
                    channel_id=subscription_data["channel_id"],
                    defaults={
                        "title": subscription_data["title"],
                        "description": subscription_data["description"],
                        "image_url": subscription_data["image_url"],
                    },
                )
                user_subscription_list.subscriptions.add(subscription)

            subscriptions_count = user_subscription_list.subscriptions.count()
            user_subscription_list.last_data_sync = timezone.now()
            user_subscription_list.save()

            return Response(
                {
                    "subscriptions_count": subscriptions_count,
                    "last_sync_date": user_subscription_list.last_data_sync,
                    "is_data_synced": True,
                }
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionsListView(generics.ListAPIView):
    """
    SubscriptionsListView - return subscription list
    * Supports filtering by specific group, 'ungroup', or 'all'.
    * Supports pagination.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Subscription.objects.all()
    serializer_class = DetailedSubscriptionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    search_fields = ["title"]
    ordering_fields = ["title"]
    filterset_class = SubscriptionFilter

    def get_queryset(self):
        return (
            self.queryset.prefetch_related("group")
            .filter(
                users_list=self.request.user.profile.user_subscription_list,
            )
            .order_by("id")
        )
