from django.db import models
from django.conf import settings
from decimal import Decimal
from device.models import Device

class Payment(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SUCCESS, 'Success'),
        (STATUS_FAILED, 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='payments')
    # amount = 15% of device.price, stored as Decimal
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    transaction_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)  # gateway tran id / val_id
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['device', 'status']),
        ]

    def __str__(self):
        return f"Payment#{self.id} {self.user.email} - {self.device.imei} - {self.status}"

    @staticmethod
    def calculate_fee_for_device(device):
        """
        Calculate 15% fee of device.price (device.price is Decimal)
        """
        if device.price is None:
            raise ValueError("Device price not set.")
        return (device.price * Decimal('0.15')).quantize(Decimal('0.01'))
