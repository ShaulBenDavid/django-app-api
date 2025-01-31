from rest_framework import serializers

from core.models import Group, UserSubscriptionCollection, Profile, User


class SharedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]


class SharedProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")

    class Meta:
        model = Profile
        fields = ["image_url", "first_name", "last_name"]


class SharedUserSubscriptionCollectionSerializer(serializers.ModelSerializer):
    user = SharedProfileSerializer()

    class Meta:
        model = UserSubscriptionCollection
        fields = ["user"]


class SharedGroupInfoSerializer(serializers.ModelSerializer):
    user_list = SharedUserSubscriptionCollectionSerializer()

    class Meta:
        model = Group
        fields = ["id", "title", "emoji", "user_list"]
