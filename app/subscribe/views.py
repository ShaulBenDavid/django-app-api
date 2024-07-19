from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError
from .filters import SubscriptionFilter
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status, generics, viewsets, filters
from core.models import Subscription, UserSubscriptionCollection, Group
from core.utils.pagination import StandardResultsSetPagination
from .serializers import (
    SubscriptionSerializer,
    GroupSerializer,
    AddSubscriptionToGroupSerializer,
)
from .utils import get_youtube_subscriptions, transform_subscriptions, get_upload_playlist_ids, get_latest_uploads, \
    get_video_details


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
                    user=request.user.profile,
                    defaults={'last_data_sync': timezone.now()},
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

            subscriptions = get_youtube_subscriptions(access_token=google_token)
            transformed_subscriptions, _ = transform_subscriptions(subscriptions=subscriptions)
            # subscriptions_playlist_ids = get_upload_playlist_ids(access_token=google_token, channel_ids=channel_ids)
            # latest_videos = get_latest_uploads(access_token=google_token, playlist_ids=subscriptions_playlist_ids)
            # video_details = get_video_details(access_token=google_token, video_ids=latest_videos)
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
                group.subscriptions.remove(subscription_to_remove)

            # Sync the fetched subscriptions with the user's subscriptions
            for subscription_data in transformed_subscriptions:
                existing_subscription = existing_subscriptions.filter(
                    channel_id=subscription_data["channel_id"]
                ).first()

                if not existing_subscription:
                    # Create a new subscription if it doesn't exist
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
            user_subscription_list.last_data_sync = timezone.now()
            user_subscription_list.save()

            return Response(
                {
                    "subscriptions_count": subscriptions_count,
                    "last_sync_date": user_subscription_list.last_data_sync,
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
    serializer_class = SubscriptionSerializer
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
        # Filter subscriptions based on the authenticated user
        return Subscription.objects.filter(
            users_list=self.request.user.profile.user_subscription_list,
        ).order_by('id')


class GroupViewSet(viewsets.ModelViewSet):
    """
    GroupViewSer - return Group items
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def create(self, request, *args, **kwargs):
        # Handle unique errors
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response(
                {"error": e.messages[0]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            if "unique constraint" in str(e):
                return Response(
                    {
                        "error": "A group with this combination of fields already exists."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"error": "Failed to create the group."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get_queryset(self):
        return (
            self.queryset.filter(
                user_list=self.request.user.profile.user_subscription_list
            )
            .order_by("-id")
            .distinct()
        )


@extend_schema(
    request=AddSubscriptionToGroupSerializer,
    responses={
        200: SubscriptionSerializer,
        400: OpenApiResponse(
            description="Failed to add subscription to a group or validation errors"
        ),
    },
)
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_subscription_to_group(request, group_id):
    """
    add_subscription_to_group - update user group with subscription
    """
    serializer = AddSubscriptionToGroupSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    subscription_id = serializer.validated_data["subscription_id"]

    group = get_object_or_404(Group, pk=group_id)
    subscription = get_object_or_404(Subscription, pk=subscription_id)

    current_group = subscription.group.filter(
        user_list=request.user.profile.user_subscription_list
    ).first()

    if subscription and group != current_group:
        group.subscriptions.add(subscription)
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(
        {"error": "Failed to add subscription to a group."},
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["DELETE"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def remove_subscription_from_group(request, subscription_id):
    """
    remove_subscription_from_group - ungroup subscriptions
    """
    subscription = get_object_or_404(Subscription, pk=subscription_id)

    group = subscription.group.filter(
        user_list=request.user.profile.user_subscription_list
    ).first()

    if group:
        group.subscriptions.remove(subscription)
        return Response(
            {"message": "Subscription removed from the group."},
            status=status.HTTP_204_NO_CONTENT,
        )

    return Response(
        {
            "error": "Subscription does not belong to any group associated with the user."
        },
        status=status.HTTP_400_BAD_REQUEST,
    )
