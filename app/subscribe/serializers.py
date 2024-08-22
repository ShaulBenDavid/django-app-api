from rest_framework import serializers

from core.models import Subscription, Group, UserSubscriptionCollection, Profile, User


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ["id", "title", "description", "channel_id", "image_url"]
        read_only_fields = ["id"]


class GroupSerializer(serializers.ModelSerializer):
    subscription_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Group
        fields = ["id", "title", "description", "emoji", "subscription_count"]
        read_only_fields = ["id", "subscription_count"]

    def create(self, validated_data):
        """Create a group."""
        user_profile = self.context["request"].user.profile

        user_subscription_collection, created = (
            UserSubscriptionCollection.objects.get_or_create(user=user_profile)
        )

        validated_data["user_list"] = user_subscription_collection
        group_instance = Group.objects.create(**validated_data)

        return group_instance


class AddSubscriptionToGroupSerializer(serializers.Serializer):
    subscription_id = serializers.IntegerField(required=True)


class SharedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]


class SharedProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
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
        fields = ["id", "title", "description", "emoji", "user_list"]
