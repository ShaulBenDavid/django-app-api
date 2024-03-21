from django.urls import path
from . import views

app_name = "user"

urlpatterns = [
    path(
        "auth/login/google/", views.GoogleLoginApi.as_view(), name="login-with-google"
    ),
    path("auth/token/", views.RefreshTokenView.as_view(), name="refresh-token"),
    path("info/", views.UserInfoView.as_view(), name="user-info"),
]
