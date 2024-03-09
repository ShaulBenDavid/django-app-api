from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
      path("auth/login/google/", views.GoogleLoginApi.as_view(),
         name="login-with-google"),
      path("auth/token/", views.RefreshTokenView, name="refresh-token"),
]
