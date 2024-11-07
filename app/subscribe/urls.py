from django.urls import path, include
from rest_framework.routers import DefaultRouter

from subscribe.views.group import (
    add_subscription_to_group,
    remove_subscription_from_group,
    GroupViewSet,
    GetGroupListView,
)
from subscribe.views.public import (
    SubscriptionGroupShareLinkViewSet,
    GetSubscriptionsFromShareLinkViewSet,
    GetGroupInfoFromShareLinkViewSet,
    GetUserGroupsView,
    GetPublicGroupSubscriptionsView,
    GetPublicGroupInfoViewSet,
)
from subscribe.views.subscriptions import SubscriptionsView, SubscriptionsListView

router = DefaultRouter()
router.register("groups", GroupViewSet)

app_name = "subscribe"

urlpatterns = [
    path("info/", SubscriptionsView.as_view(), name="subscriptions-view"),
    path("list/", SubscriptionsListView.as_view(), name="subscriptions-list-view"),
    path(
        "groups/<int:group_id>/add-subscription/",
        add_subscription_to_group,
        name="add_subscription_to_group",
    ),
    path(
        "subs/<int:subscription_id>/ungroup-subscription/",
        remove_subscription_from_group,
        name="remove_subscription_from_group",
    ),
    path("groups/detailed/", GetGroupListView.as_view(), name="detailed_group_list"),
    # Public
    path(
        "group-share-link/",
        SubscriptionGroupShareLinkViewSet.as_view(),
        name="share-link",
    ),
    path(
        "shared-subscriptions/",
        GetSubscriptionsFromShareLinkViewSet.as_view(),
        name="shared-subscriptions",
    ),
    path(
        "shared-group/info/",
        GetGroupInfoFromShareLinkViewSet.as_view(),
        name="shared-group-info",
    ),
    path(
        "user/groups/<str:username>/",
        GetUserGroupsView.as_view(),
        name="get-public-user-groups",
    ),
    path(
        "public-user/<int:user_id>/group/<int:group_id>/subscriptions/",
        GetPublicGroupSubscriptionsView.as_view(),
        name="get-public-group-subscriptions",
    ),
    path(
        "public-user/<int:user_id>/group/<int:group_id>/info/",
        GetPublicGroupInfoViewSet.as_view(),
        name="get-public-group-info",
    ),
    path("", include(router.urls)),
]
