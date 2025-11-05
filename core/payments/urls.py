from django.urls import path
from .views import CreatePaymentView, PaymentWebhookView, PaymentSuccessView, PaymentFailView, PaymentCancelView

urlpatterns = [
    path('create/', CreatePaymentView.as_view(), name='payments-create'),
    path('webhook/', PaymentWebhookView.as_view(), name='payments-webhook'),
    path('success/', PaymentSuccessView.as_view(), name='payments-success'),
    path('fail/', PaymentFailView.as_view(), name='payments-fail'),
    path('cancel/', PaymentCancelView.as_view(), name='payments-cancel'),
]
