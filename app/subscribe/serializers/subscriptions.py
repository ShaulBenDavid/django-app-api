from core.models import Subscription
from rest_framework import serializers


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ["id", "title", "description", "channel_id", "image_url"]
        read_only_fields = ["id"]
