from rest_framework import generics, permissions,status
from .models import Device
from .serializers import DeviceSerializer,DeviceDetailedSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from .utils import get_object

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





class DeviceDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

   
    def get(self, request, pk):
        device = get_object(pk, request.user)
        serializer = DeviceDetailedSerializer(device)
        return Response({'success': True, 'data': serializer.data}, status=200)

    def put(self, request, pk):
        device = get_object(pk, request.user)
        serializer = DeviceSerializer(device, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'Device updated', 'data': serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        device = get_object(pk, request.user)
        device.delete()
        return Response({'success': True, 'message': 'Device deleted'}, status=204)

