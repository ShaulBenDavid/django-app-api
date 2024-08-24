from django.db.models import Count
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status, viewsets
from core.models import Subscription, Group
from subscribe.serializers.group import (
    AddSubscriptionToGroupSerializer,
    GroupSerializer,
)
from subscribe.serializers.subscriptions import SubscriptionSerializer


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
        user_subscription_list = self.request.user.profile.user_subscription_list
        return (
            self.queryset.filter(user_list=user_subscription_list)
            .annotate(subscription_count=Count("subscriptions"))
            .order_by("title")
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
    user_subscription_list = request.user.profile.user_subscription_list

    group = get_object_or_404(Group, pk=group_id, user_list=user_subscription_list)
    subscription = get_object_or_404(
        Subscription, pk=subscription_id, users_list=user_subscription_list
    )

    current_group = subscription.group.filter(user_list=user_subscription_list).first()

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
            data={"message": "Subscription removed from the group."},
            status=status.HTTP_200_OK,
        )

    return Response(
        {
            "error": "Subscription does not belong to any group associated with the user."
        },
        status=status.HTTP_400_BAD_REQUEST,
    )
