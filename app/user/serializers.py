from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from core.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "image_url"]


class UserInfoSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="profile.username")
    image_url = serializers.URLField(source="profile.image_url")

    class Meta:
        model = User
        fields = ["username", "image_url", "email", "first_name", "last_name"]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user, **kwargs):
        token = super().get_token(user)
        return token
