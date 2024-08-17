from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("groups", views.GroupViewSet)

app_name = "subscribe"

urlpatterns = [
    path("info/", views.SubscriptionsView.as_view(), name="subscriptions-view"),
    path(
        "list/", views.SubscriptionsListView.as_view(), name="subscriptions-list-view"
    ),
    path(
        "groups/<int:group_id>/add-subscription/",
        views.add_subscription_to_group,
        name="add_subscription_to_group",
    ),
    path(
        "subs/<int:subscription_id>/ungroup-subscription/",
        views.remove_subscription_from_group,
        name="remove_subscription_from_group",
    ),
    path(
        "group-share-link/",
        views.SubscriptionGroupShareLinkViewSet.as_view(),
        name="share-link",
    ),
    path(
        "shared-subscriptions/",
        views.GetSubscriptionsFromShareLinkViewSet.as_view(),
        name="shared-subscriptions",
    ),
    path(
        "shared-group/info/",
        views.GetGroupInfoFromShareLinkViewSet.as_view(),
        name="shared-group-info",
    ),
    path("", include(router.urls)),
]
