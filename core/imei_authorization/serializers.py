# device/serializers.py

from rest_framework import serializers
from .models import AuthorizedIMEI

class AuthorizedIMEISerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorizedIMEI
        fields = ['id', 'imei', 'created_at']

        read_only_fields = ['id', 'created_at']

    def validate_imei(self,value):
        if AuthorizedIMEI.objects.filter(imei=value).exists():
            raise serializers.ValidationError("This IMEI exists.")
        return value
