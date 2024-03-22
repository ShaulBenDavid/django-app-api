from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.conf import settings
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from app import settings
from .utils import get_youtube_subscriptions


@csrf_exempt  # This decorator is used to allow POST requests without CSRF tokens
def subscriptions_view(request):
    if request.method == 'POST':
        access_token = request.POST.get('access_token')
        if access_token:
            subscriptions = get_youtube_subscriptions(access_token)
            return JsonResponse({'subscriptions': subscriptions})
        else:
            return JsonResponse({'error': 'Access token is missing'}, status=400)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

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
        try:
            refresh_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"])
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            refresh = RefreshToken(refresh_token)
            access_token = refresh["google_token"]

            if access_token:
                subscriptions = get_youtube_subscriptions(access_token)
                return JsonResponse({'subscriptions': subscriptions})
            else:
                return JsonResponse({'error': 'Access token is missing'}, status=400)
        except Exception as e:
            return Response({"error": e}, status=status.HTTP_401_UNAUTHORIZED)
