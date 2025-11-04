from rest_framework import generics, permissions
from .models import Device
from .serializers import DeviceSerializer

class DeviceListCreateView(generics.ListCreateAPIView):
    """
    users can create device objects.
    only admin and staff can view all the devices
    normal user can view there own devices only
    """
    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Device.objects.all()
        return Device.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

