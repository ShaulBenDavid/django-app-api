from http import HTTPStatus
import random
from urllib.parse import urlencode

from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import serializers, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import filters
from django.conf import settings
from django.shortcuts import redirect
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from core.utils.auth import IsCreator
from core.utils.pagination import StandardResultsSetPagination
from user.mixins import PublicApiMixin, ApiErrorsMixin
from user.utils import (
    google_get_tokens,
    google_get_user_info,
    generate_tokens_for_user,
    google_refresh_access_token,
)
from core.models import User, Profile, CustomURL
from rest_framework import status
from user.serializers import (
    UserInfoSerializer,
    UserProfileSerializer,
    PublicUserProfileSerializer,
    UserCustomLinksSerializer,
    GetPublicUserProfileSerializer,
)


@extend_schema(
    parameters=[
        OpenApiParameter(
            "code",
            OpenApiTypes.STR,
            description="Enter the token you get from Google.",
            required=False,
        ),
        OpenApiParameter(
            "error",
            OpenApiTypes.STR,
            description="Error message from Google.",
            required=False,
        ),
    ]
)
class GoogleLoginApi(PublicApiMixin, ApiErrorsMixin, APIView):
    class InputSerializer(serializers.Serializer):
        code = serializers.CharField(required=False)
        error = serializers.CharField(required=False)

    serializer_class = InputSerializer

    def get(self, request, *args, **kwargs):
        input_serializer = self.InputSerializer(data=request.GET)
        input_serializer.is_valid(raise_exception=True)

        validated_data = input_serializer.validated_data

        code = validated_data.get("code")
        error = validated_data.get("error")

        login_url = f"{settings.GOOGLE_OAUTH2_REDIRECT}"

        if error or not code:
            params = urlencode({"error": error})
            return redirect(f"{login_url}?{params}")

        redirect_uri = f"{settings.GOOGLE_OAUTH2_REDIRECT}/google"
        google_access_token, google_refresh_token = google_get_tokens(
            code=code, redirect_uri=redirect_uri
        )

        user_data = google_get_user_info(access_token=google_access_token)

        try:
            user = User.objects.get(email=user_data["email"])
        except User.DoesNotExist:
            user = self._create_user(user_data)

        access_token, refresh_token = generate_tokens_for_user(user)
        response_data = {
            "access_token": str(access_token),
            "google_token": str(google_access_token),
            "role": user.role,
        }
        response = Response(response_data, status=status.HTTP_200_OK)
        response.set_cookie(
            key=settings.SIMPLE_JWT["AUTH_COOKIE"],
            value=str(refresh_token),
            secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
            httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
            samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
            max_age=settings.SIMPLE_JWT["AUTH_COOKIE_MAX_AGE"],
        )
        response.set_cookie(
            key=settings.SIMPLE_JWT["AUTH_GOOGLE_COOKIE"],
            value=str(google_refresh_token),
            secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
            httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
            samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
            max_age=settings.SIMPLE_JWT["AUTH_COOKIE_MAX_AGE"],
        )
        return response

    def _create_user(self, user_data):
        first_name = user_data.get("given_name", "")
        last_name = user_data.get("family_name", "")

        email = user_data["email"]
        username_base = email.split("@")[0]
        random_digits = str(random.randint(10, 99))
        username = f"{username_base}{random_digits}"

        return User.objects.create(
            email=email,
            username=username,
            image_url=user_data["picture"],
            first_name=first_name,
            last_name=last_name,
            registration_method="google",
        )


class RefreshTokenView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "refresh",
                OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                required=True,
                description="The refresh token to be used for token refresh.",
            ),
        ],
        responses={
            200: "tokens refreshed",
            400: "Refresh token has expired or is invalid",
            401: "Refresh token has expired or is invalid",
        },
    )
    def get(self, request):
        """
        Refresh the access token using the provided refresh token from a cookie
        """
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"])
        google_refresh_token = request.COOKIES.get(
            settings.SIMPLE_JWT["AUTH_GOOGLE_COOKIE"]
        )

        if not refresh_token or not google_refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            refresh = RefreshToken(refresh_token)
            google_access = google_refresh_access_token(google_refresh_token)
            access_token = str(refresh.access_token)
            user_id = refresh.access_token.payload.get("user_id", None)
            user = User.objects.get(id=user_id)
            user.last_login = timezone.now()
            user.save()

            response_data = {
                "access_token": str(access_token),
                "google_token": str(google_access),
                "role": user.role,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {"error": "Refresh token has expired"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "refresh",
                OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                required=True,
                description="The refresh token to be used for token refresh.",
            ),
        ],
        responses={200: "Logout successful"},
    )
    def delete(self, request):
        """
        Logout and delete the refresh token cookie
        """
        response = Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        response.set_cookie(
            key=settings.SIMPLE_JWT["AUTH_COOKIE"],
            value="",
            expires=0,
            secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
            httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
            samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        )
        response.set_cookie(
            key=settings.SIMPLE_JWT["AUTH_GOOGLE_COOKIE"],
            value="",
            expires=0,
            secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
            httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
            samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        )
        return response


class UserInfoView(generics.RetrieveAPIView):
    serializer_class = UserInfoSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserProfileView(APIView):
    serializer_class = UserProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = self.serializer_class(profile)
        return Response(serializer.data, status=HTTPStatus.OK)

    def patch(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = self.serializer_class(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = User.objects.get(id=request.user.id)
        user.delete()
        return Response("User deleted successfully", status=HTTPStatus.OK)


class UserCustomLinksView(APIView):
    serializer_class = UserCustomLinksSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsCreator]

    def get(self, request):
        profile = Profile.objects.prefetch_related("custom_urls").get(user=request.user)
        custom_links = profile.custom_urls.all()
        serializer = self.serializer_class(custom_links, many=True)

        return Response({"custom_urls": serializer.data})

    def patch(self, request):
        profile = Profile.objects.get(user=request.user)

        custom_links_data = request.data.get("custom_urls", [])

        serializer = self.serializer_class(data=custom_links_data, many=True)

        if serializer.is_valid():
            updated_custom_urls = []

            for link_data in serializer.validated_data:
                link, created = CustomURL.objects.update_or_create(
                    url=link_data.get("url"),
                    defaults={"name": link_data.get("name"), "profile": profile},
                )
                updated_custom_urls.append(link)

            current_urls = profile.custom_urls.all()
            current_urls_to_keep = set(updated_custom_urls)

            for url in current_urls:
                if url not in current_urls_to_keep:
                    url.delete()

            profile.custom_urls.set(updated_custom_urls)

            profile.save()

            updated_serializer = self.serializer_class(updated_custom_urls, many=True)
            return Response({"custom_urls": updated_serializer.data})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetPublicUserProfileView(APIView):
    queryset = Profile.objects.all()
    serializer_class = PublicUserProfileSerializer

    def get(self, request, username=None):
        try:
            user = (
                self.queryset.select_related("user")
                .prefetch_related("custom_urls")
                .get(username=username, is_public=True)
            )

        except Profile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetPublicUsersView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = GetPublicUserProfileSerializer
    pagination_class = StandardResultsSetPagination
    queryset = Profile.objects.all()
    filter_backends = [
        filters.SearchFilter,
    ]
    search_fields = ["username"]

    def get_queryset(self):
        search_query = self.request.query_params.get("search")
        return self.queryset.filter(
            is_public=True, username__icontains=search_query
        ).order_by('id')
