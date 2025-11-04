from rest_framework import serializers
from .models import Device
from accounts.serializers import UserSerializer

class DeviceSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    class Meta:
        model = Device
        fields = ['id', 'owner', 'name', 'type', 'os', 'description', 'image', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']


class DeviceDetailedSerializer(serializers.ModelSerializer):
    owner=UserSerializer()
    image = serializers.ImageField(required=False)

    class Meta:
        model = Device
        fields = ['id', 'owner', 'name', 'type', 'os', 'description', 'image', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']
