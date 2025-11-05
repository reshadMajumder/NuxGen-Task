from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField

class Device(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='devices')
    name = models.CharField(max_length=100)
    imei = models.CharField(max_length=50, unique=True,blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    price=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    os = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = CloudinaryField('device_image', blank=True, null=True)
    is_authorized= models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.owner.email}"
