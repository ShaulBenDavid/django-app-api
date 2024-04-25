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
    path("", include(router.urls)),
]
