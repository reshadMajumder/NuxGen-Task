from django.db import models

# Create your models here.
class AuthorizedIMEI(models.Model):
    imei = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.imei