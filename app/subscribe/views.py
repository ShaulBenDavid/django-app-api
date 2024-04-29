from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status, generics, viewsets, filters
from core.models import Subscription, UserSubscriptionCollection, Group
from core.utils.pagination import StandardResultsSetPagination
from .serializers import SubscriptionSerializer, GroupSerializer
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
    * Have pagination.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ["title"]
    ordering_fields = ["title"]

    def get_queryset(self):
        # Filter subscriptions based on the authenticated user
        return Subscription.objects.filter(
            users_list=self.request.user.profile.user_subscription_list
        )


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
        except Exception as e:
            if 'unique constraint' in str(e):
                return Response(
                    {"error": "A group with this combination of fields already exists."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    {"error": "Failed to create the group."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

    def get_queryset(self):
        return (
            self.queryset.filter(
                user_list=self.request.user.profile.user_subscription_list
            )
            .order_by("-id")
            .distinct()
        )


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_subscription_to_group(request, group_id):
    """
    add_subscription_to_group - update user group with subscription
    """
    group = get_object_or_404(Group, pk=group_id)
    subscription_id = request.data.get('subscription_id')

    if not subscription_id:
        return Response({'error': 'subscription_id is required'}, status=status.HTTP_400_BAD_REQUEST)


    subscription = get_object_or_404(Subscription, pk=subscription_id)
    if subscription:
        group.subscriptions.add(subscription)

        return Response('subscription', status=status.HTTP_200_OK)

    return Response('1', status=status.HTTP_400_BAD_REQUEST)
