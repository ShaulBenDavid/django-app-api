from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from core.models import User, Profile, CustomURL


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
        token["role"] = user.role
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
            "tiktok_url",
            "telegram_url",
            "is_public",
            "description",
        ]
        read_only_fields = ["id"]


class UserCustomLinksSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomURL
        fields = [
            "name",
            "url",
        ]
        read_only_fields = ["id"]


class PublicUserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    custom_urls = UserCustomLinksSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = [
            "username",
            "instagram_url",
            "twitter_url",
            "linkedin_url",
            "youtube_url",
            "tiktok_url",
            "telegram_url",
            "is_public",
            "description",
            "id",
            "user",
            "custom_urls",
        ]
        read_only_fields = ["username", "id"]


class GetPublicUserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ["username", "image_url", "id", "description"]
