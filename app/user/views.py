from urllib.parse import urlencode

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import serializers
from rest_framework.views import APIView
from django.conf import settings
from django.shortcuts import redirect
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from user.mixins import PublicApiMixin, ApiErrorsMixin
from user.utils import google_get_access_token, google_get_user_info, generate_tokens_for_user
from core.models import User
from rest_framework import status
from user.serializers import UserSerializer


@extend_schema(
    parameters=[
        OpenApiParameter(
            'code',
            OpenApiTypes.STR,
            description='Enter the token you get from Google.',
            required=False,
        ),
        OpenApiParameter(
            'error',
            OpenApiTypes.STR,
            description='Error message from Google.',
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

        code = validated_data.get('code')
        error = validated_data.get('error')

        login_url = f'{settings.BASE_FRONTEND_URL}'

        if error or not code:
            params = urlencode({'error': error})
            return redirect(f'{login_url}?{params}')

        redirect_uri = f'{settings.BASE_FRONTEND_URL}/google'
        access_token = google_get_access_token(code=code,
                                               redirect_uri=redirect_uri)

        user_data = google_get_user_info(access_token=access_token)

        try:
            user = User.objects.get(email=user_data['email'])
        except User.DoesNotExist:
            user = self._create_user(user_data)

        access_token, refresh_token = generate_tokens_for_user(user)
        response_data = {
            'user': UserSerializer(user).data,
            'access_token': str(access_token),
        }
        response = Response(response_data, status=status.HTTP_200_OK)
        response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                value=str(refresh_token),
                expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'])
        return response

    def _create_user(self, user_data):
        first_name = user_data.get('given_name', '')
        last_name = user_data.get('family_name', '')

        return User.objects.create(
            email=user_data['email'],
            username=user_data['email'],
            image_url=user_data['picture'],
            first_name=first_name,
            last_name=last_name,
            registration_method='google'
        )


class RefreshTokenView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(
                'refresh',
                OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                required=True,
                description='The refresh token to be used for token refresh.',
            ),
        ],
        responses={
            200: UserSerializer(many=False),
            400: 'Refresh token has expired or is invalid',
            401: 'Refresh token has expired or is invalid',
        }
    )
    def get(self, request):
        """
        Refresh the access token using the provided refresh token from a cookie
        """
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])

        if not refresh_token:
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
            user_data = User.objects.get(id=refresh['user_id'])
            access_token = str(refresh.access_token)

            response_data = {
                'user': UserSerializer(user_data).data,
                'access_token': str(access_token),
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Refresh token has expired'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': e}, status=status.HTTP_401_UNAUTHORIZED)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                'refresh',
                OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                required=True,
                description='The refresh token to be used for token refresh.',
            ),
        ],
        responses={200: 'Logout successful'},
    )
    def delete(self, request):
        """
        Logout and delete the refresh token cookie
        """
        response = Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        response.set_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE'],
            value='',
            expires=0,
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'])
        return response
