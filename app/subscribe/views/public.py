from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from rest_framework.generics import get_object_or_404, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status, generics
from core.models import Subscription, Group
from core.utils.pagination import StandardResultsSetPagination
from subscribe.serializers.group import GroupListSerializer
from subscribe.serializers.subscriptions import (
    SubscriptionSerializer,
)
from subscribe.serializers.public import (
    SharedGroupInfoSerializer,
)
from subscribe.utils.public import (
    generate_temp_group_url,
    validate_temp_group_url,
)


class SubscriptionGroupShareLinkViewSet(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="group_id",
                type=OpenApiTypes.STR,
                description="ID of the group to share",
                required=True,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="path",
                type=OpenApiTypes.STR,
                description="The path for the temporary group URL",
                required=True,
                location=OpenApiParameter.QUERY,
            ),
        ],
    )
    def get(self, request):
        group_id = request.query_params.get("group_id", None)
        path = request.query_params.get("path", None)

        if not group_id or not path:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"error": "group_id/path is required"},
            )

        try:
            group = get_object_or_404(
                Group,
                pk=group_id,
                user_list=request.user.profile.user_subscription_list,
            )
            group_share_link = generate_temp_group_url(
                path=path, group_id=group.pk, user_list_id=group.user_list.id
            )

            return Response(data={"link": group_share_link}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"error": "Failed to create the group share link."},
            )


class GetSubscriptionsFromShareLinkViewSet(ListAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="token",
                type=OpenApiTypes.STR,
                description="ID of the group to share",
                required=True,
                location=OpenApiParameter.QUERY,
            ),
        ],
    )
    def get_queryset(self):
        token = self.request.query_params.get("token", None)
        if not token:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"error": "token is required"},
            )

        try:
            group_id, user_list_id, _ = validate_temp_group_url(token=token)
            return self.queryset.filter(
                group__id=group_id,
                users_list__id=user_list_id,
            ).order_by("id")

        except Exception as e:
            return Subscription.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"error": "Failed to fetch group or no subscriptions found."},
            )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class GetGroupInfoFromShareLinkViewSet(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="token",
                type=OpenApiTypes.STR,
                description="ID of the group to share",
                required=True,
                location=OpenApiParameter.QUERY,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        token = self.request.query_params.get("token", None)
        if not token:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"error": "token is required"},
            )

        try:
            group_id, user_list_id, expiration = validate_temp_group_url(token=token)

            group = Group.objects.select_related("user_list__user__user").get(
                pk=group_id, user_list=user_list_id
            )

            serializer = SharedGroupInfoSerializer(group)

            response_data = serializer.data
            response_data["expiration_date"] = expiration

            return Response(data=response_data, status=status.HTTP_200_OK)

        except Group.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND, data={"error": "Group not found"}
            )
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": str(e)})


class GetUserGroupsView(generics.ListAPIView):
    """
    GetUserGroupsView - return groups with subscription list
    * Supports pagination.
    """

    queryset = Group.objects.all()
    serializer_class = GroupListSerializer
    pagination_class = StandardResultsSetPagination
    search_fields = ["title"]
    ordering_fields = ["title"]

    def get_queryset(self):
        username = self.kwargs.get("username")
        self.pagination_class.page_size = 5

        return (
            self.queryset.select_related("user_list__user")
            .prefetch_related("subscriptions")
            .filter(
                user_list__user__username=username,
                user_list__user__is_public=True,
                is_public=True,
            )
            .order_by("id")
        )
