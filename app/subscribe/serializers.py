from rest_framework import serializers
from core.models import Subscription, Group


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ["title", "description", "channel_id", "image_url"]


class GroupSerializer(serializers.ModelSerializer):
    subscription_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ["id", "title", "description", "subscription_count"]

    def get_subscription_count(self, obj):
        return obj.subscriptions.count()
