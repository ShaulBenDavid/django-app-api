from django.urls import path
from . import views

app_name = "subscribe"

urlpatterns = [
    path("info/", views.SubscriptionsView.as_view(), name="subscriptions-view"),
]
