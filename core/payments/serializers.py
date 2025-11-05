from rest_framework import serializers
from .models import Payment
from device.models import Device
from decimal import Decimal

class CreatePaymentSerializer(serializers.ModelSerializer):
    device_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'device_id', 'amount', 'status', 'transaction_id', 'created_at']
        read_only_fields = ['id', 'amount', 'status', 'transaction_id', 'created_at']

    def validate_device_id(self, value):
        user = self.context['request'].user
        try:
            device = Device.objects.get(id=value, owner=user)
        except Device.DoesNotExist:
            raise serializers.ValidationError("Device not found or not owned by you.")
        if device.is_authorized:
            raise serializers.ValidationError("Device is already authorized.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        device = Device.objects.get(id=validated_data['device_id'], owner=user)
        amount = Payment.calculate_fee_for_device(device)  # 15% of device price
        payment = Payment.objects.create(user=user, device=device, amount=amount, status=Payment.STATUS_PENDING)
        return payment
