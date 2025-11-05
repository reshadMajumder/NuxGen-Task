from rest_framework import generics, permissions,status
from .models import Device
from .serializers import DeviceSerializer,DeviceDetailedSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from .utils import get_object
from imei_authorization.models import AuthorizedIMEI


class DeviceListCreateView(generics.ListCreateAPIView):
    """
    Users can create device objects.
    Only admin and staff can view all devices.
    Normal users can view their own devices only.
    Supports filtering by authorization status.
    """
    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Device.objects.select_related('owner').all() if (user.is_staff or user.is_superuser) else Device.objects.select_related('owner').filter(owner=user)
        
        is_authorized = self.request.query_params.get('is_authorized')
        if is_authorized is not None:
            if is_authorized.lower() in ['true', '1']:
                queryset = queryset.filter(is_authorized=True)
            elif is_authorized.lower() in ['false', '0']:
                queryset = queryset.filter(is_authorized=False)

        return queryset

    def perform_create(self, serializer):
        imei = serializer.validated_data.get('imei')
        # check if IMEI exists in AuthorizedIMEI table
        is_authorized = AuthorizedIMEI.objects.filter(imei=imei).exists()
        serializer.save(owner=self.request.user, is_authorized=is_authorized)



class DeviceDetailAPIView(APIView):
    """
    API View to retrieve, update, or delete a single Device.
    Permissions:
    - Only authenticated users can access.
    - Normal users can only access their own devices.
    - Staff/Admin can access all devices.

    """
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

