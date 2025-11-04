
from django.urls import path
from .views import AuthorizedIMEIListCreateView, AuthorizedIMEIDeleteView

urlpatterns = [
    path('', AuthorizedIMEIListCreateView.as_view(), name='authorized-imei-list-create'),
    path('<int:pk>/', AuthorizedIMEIDeleteView.as_view(), name='authorized-imei-delete'),
]
