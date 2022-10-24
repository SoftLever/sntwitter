from rest_framework import serializers
from user.models import Servicenow, CustomFields


class CustomFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomFields
        fields = ['id', 'field_name', 'message', 'user']


class ServicenowSerializer(serializers.ModelSerializer):
    admin_password = serializers.CharField(
        max_length=128,
        style={'input_type': 'password'}
    )

    class Meta:
        model = Servicenow
        fields = ('id', 'instance_url', 'admin_user', 'admin_password', 'user')

    def create(self, validated_data):
        sn = Servicenow(**validated_data)
        sn.save()
        return sn

    def update(self, instance, validated_data):
        instance.instance_url = validated_data.get('instance_url', instance.instance_url)
        instance.admin_user = validated_data.get('admin_user', instance.admin_user)
        instance.admin_password = validated_data.get('admin_password', instance.admin_password)
        instance.save()
        return instance
