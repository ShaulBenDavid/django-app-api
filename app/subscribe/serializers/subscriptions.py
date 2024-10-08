from core.models import Subscription, Group
from rest_framework import serializers


class SubscriptionGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "title"]


class DetailedSubscriptionSerializer(serializers.ModelSerializer):
    group = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ["id", "title", "description", "channel_id", "image_url", "group"]

    def get_group(self, obj):
        request = self.context.get("request")
        if request and request.user and hasattr(request.user, "profile"):
            user_subscription_list = request.user.profile.user_subscription_list

            # Filter groups to include only those associated with the current user's subscription list
            user_group = obj.group.filter(user_list=user_subscription_list).first()
            if not user_group:
                return None
            serializer = SubscriptionGroupSerializer(user_group, many=False)
            return serializer.data
        return None


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ["id", "title", "description", "channel_id", "image_url"]
        read_only_fields = ["id"]
