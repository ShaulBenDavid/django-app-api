from rest_framework import serializers

from core.models import Subscription, Group, UserSubscriptionCollection, Profile


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


class SharedProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["username", "image_url"]


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
