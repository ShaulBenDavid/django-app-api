from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from django.contrib import admin
from django.urls import path, include
# from django_otp.admin import OTPAdminSite

from core import views as core_views


# admin.site.__class__ = OTPAdminSite

urlpatterns = [
    path("shon/", admin.site.urls),
    path("api/health-check/", core_views.health_check, name="health-check"),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
    path("api/user/", include("user.urls")),
    path("api/subscribe/", include("subscribe.urls")),
]
