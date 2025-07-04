from django.urls import path
from . import views

app_name = "user"

urlpatterns = [
    path(
        "auth/login/google/", views.GoogleLoginApi.as_view(), name="login-with-google"
    ),
    path("auth/token/", views.RefreshTokenView.as_view(), name="refresh-token"),
    path("info/", views.UserInfoView.as_view(), name="user-info"),
    path("profile/", views.UserProfileView.as_view(), name="user-profile"),
    path("custom-links/", views.UserCustomLinksView.as_view(), name="user-profile"),
    path(
        "profile/<str:username>/",
        views.GetPublicUserProfileView.as_view(),
        name="get-user-profile",
    ),
    path("list/", views.GetPublicUsersView.as_view(), name="user-list"),
]
