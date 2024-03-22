from django.urls import path
from . import views

app_name = "subscribe"

urlpatterns = [
    path("user/", views.SubscriptionsView.as_view(), name="subscriptions-view"),
]
