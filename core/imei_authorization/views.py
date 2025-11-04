from django.shortcuts import render

# Create your views here.
# device/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from core.permissions import IsAdmin, IsStaff
from .models import AuthorizedIMEI
from .serializers import AuthorizedIMEISerializer
from device.models import Device

class AuthorizedIMEIListCreateView(APIView):
    """
    admin and staff can create
    admin and staff can get list
    """
    permission_classes = [IsAuthenticated, (IsAdmin | IsStaff)]

    def get(self, request):
        imeis = AuthorizedIMEI.objects.all()
        serializer = AuthorizedIMEISerializer(imeis, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = AuthorizedIMEISerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AuthorizedIMEIDeleteView(APIView):
    """
    only admin can delete
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def delete(self, request, pk):
        try:
            imei = AuthorizedIMEI.objects.get(pk=pk)
            if imei in Device.objects.filter(imei=imei.imei):
                return Response({"detail": "Cannot delete authorized IMEI linked to a device."}, status=400)
        except AuthorizedIMEI.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)

        imei.delete()
        return Response({"detail": "Deleted Successfully"}, status=status.HTTP_204_NO_CONTENT)
