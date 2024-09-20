from rest_framework import serializers

from core.models import Group, UserSubscriptionCollection
from subscribe.serializers.subscriptions import SubscriptionSerializer


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


class GroupListSerializer(serializers.ModelSerializer):
    subscriptions = serializers.SerializerMethodField()
    subscriptions_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ["id", "title", "emoji", "subscriptions", "subscriptions_count"]

    def get_subscriptions(self, obj):
        subscriptions = obj.subscriptions.all()[:5]
        return SubscriptionSerializer(subscriptions, many=True).data

    def get_subscriptions_count(self, obj):
        return obj.subscriptions.count()
