from django.urls import path
from . import views

urlpatterns = [
      path("auth/login/google/", views.GoogleLoginApi.as_view(),
         name="login-with-google"),
]
