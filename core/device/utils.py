from .models import Device
from .serializers import DeviceSerializer
from rest_framework.exceptions import NotFound, PermissionDenied


def get_object(pk, user):
    """
    helper function for role based object task 
    """
    try:
        device = Device.objects.select_related('owner').get(pk=pk)
    except Device.DoesNotExist:
        raise NotFound("Device not found")

    # only owner or staff/admin
    if (device.owner != user) and (not user.is_staff) and (not user.is_superuser):
        raise PermissionDenied("You are not allowed to modify this device.")

    return device
