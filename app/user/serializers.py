from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from core.models import User, Profile


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


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = [
            "username",
            "instagram_url",
            "twitter_url",
            "linkedin_url",
            "youtube_url",
            "is_public",
            "description",
        ]
        read_only_fields = ["username"]


class PublicUserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "username",
            "instagram_url",
            "twitter_url",
            "linkedin_url",
            "youtube_url",
            "is_public",
            "description",
            "user",
        ]
        read_only_fields = ["username"]
