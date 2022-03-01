from rest_framework import serializers
from user.models import Twitter


class TwitterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Twitter
        fields = ('id', 'handle', 'userid', 'profile_image', 'subscription_id')
