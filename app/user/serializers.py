from rest_framework import serializers
from core.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'image_url']


class UserInfoSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='profile.username')
    image_url = serializers.URLField(source='profile.image_url')

    class Meta:
        model = User
        fields = ['username', 'image_url', 'email', 'first_name', 'last_name']
