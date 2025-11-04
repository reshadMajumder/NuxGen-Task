from rest_framework import serializers
from .models import Device
from accounts.serializers import UserSerializer



class DeviceSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    imei = serializers.CharField(required=True)
    price=serializers.DecimalField(max_digits=10, decimal_places=2, required=True)

    class Meta:
        model = Device
        fields = ['id', 'owner', 'name','imei', 'type', 'os','price', 'description','is_authorized', 'image', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at','is_authorized', 'updated_at']

    # imei should be unique
    def validate_imei(self, value):
        if Device.objects.filter(imei=value).exists():
            raise serializers.ValidationError("Device with this IMEI already exists.")
        return value
    
    def validate_price(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Price must be a positive number.")
        return value



class DeviceDetailedSerializer(serializers.ModelSerializer):
    owner=UserSerializer()
    image = serializers.ImageField(required=False)

    class Meta:
        model = Device
        fields = ['id', 'owner', 'name','imei', 'type', 'os','price', 'is_authorized', 'description', 'image', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at','is_authorized', 'updated_at']



