from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.conf import settings
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from app import settings
from .utils import get_youtube_subscriptions, transform_subscriptions


class SubscriptionsView(APIView):
    """
    SubscriptionsView - handle user subscribers.
    * Requires token authentication.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Return a list of all user subscriptions.
        """
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"])
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            refresh = RefreshToken(refresh_token)
            access_token = refresh["google_token"]

            if not access_token:
                return Response({"error": "Access token is missing"}, status=400)

            subscriptions = get_youtube_subscriptions(access_token)
            transformed_subscriptions = transform_subscriptions(subscriptions)
            return Response({"subscriptions": transformed_subscriptions})

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
