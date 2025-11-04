from django.urls import path
from . views import DeviceListCreateView,DeviceDetailAPIView
urlpatterns = [
    path('', DeviceListCreateView.as_view(), name='device-list-create'),
    path('<int:pk>/', DeviceDetailAPIView.as_view(), name='device-detail'),

    
]