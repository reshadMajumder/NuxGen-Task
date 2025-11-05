

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import CreatePaymentSerializer,PaymentDetailSerializer
from .models import Payment
from .services import get_adapter
from imei_authorization.models import AuthorizedIMEI
from decimal import Decimal
from core.permissions import IsAdmin, IsStaff
# import logging

# logger = logging.getLogger(__name__)

class CreatePaymentView(generics.CreateAPIView):
    """
    Create payment record and initialize provider (SSLCommerz).
    Request body: { "device_id": <id> }
    Response: { payment_id, amount, payment_url }
    """
    serializer_class = CreatePaymentSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response({"detail": "Validation failed", "errors": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
        payment = serializer.save()
        # Refetch with select_related 
        payment = Payment.objects.select_related('user', 'device').get(id=payment.id)

        adapter = get_adapter('sslcommerz')

        # URLs - in development use ngrok domain with https
        domain = getattr(settings, 'PUBLIC_DOMAIN', 'http://127.0.0.1:8000')
        return_urls = {
            'success': f"{domain}/api/v1/payments/success/",   # optional front-end endpoints
            'fail': f"{domain}/api/v1/payments/fail/",
            'cancel': f"{domain}/api/v1/payments/cancel/"
        }
        ipn_url = f"{domain}/api/v1/payments/webhook/"  # SSLCommerz will call this

        try:
            res = adapter.init_payment(payment, return_urls=return_urls, ipn_url=ipn_url)
        except Exception as e:
            # logger.exception("SSLCommerz init error")
            payment.status = Payment.STATUS_FAILED
            payment.save()
            return Response({"detail": "Failed to initialize payment", "error": str(e)},
                            status=status.HTTP_502_BAD_GATEWAY)

        # if provider returns success
        if res.get('status') == 'SUCCESS' and res.get('GatewayPageURL'):
            return Response({
                "payment_id": payment.id,
                "amount": str(payment.amount),
                "payment_url": res.get('GatewayPageURL'),
                "raw": res  #we will remove in prod
            })
        else:
            payment.status = Payment.STATUS_FAILED
            payment.save()
            return Response({"detail": "Payment initialization failed", "provider_response": res}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class PaymentWebhookView(APIView):
    """
    Endpoint to receive SSLCommerz IPN/webhook.
    SSLCommerz will POST to this endpoint. No authentication (AllowAny).
    """
    permission_classes = [AllowAny]
    throttle_classes = []  # Disable throttling for webhook (external service)

    def post(self, request, *args, **kwargs):
        data = request.data or request.POST.dict()
        adapter = get_adapter('sslcommerz')
        info = adapter.verify_payload(data)
        tran_id = info.get('tran_id')
        status_received = (info.get('status') or '').upper()
        # print("===============================accesed webhook=====================================")

        if not tran_id:
            # logger.warning("Webhook without tran_id: %s", data)
            return Response({"detail": "tran_id missing"}, status=400)

        try:
            payment = Payment.objects.select_related('device').get(id=tran_id)
        except Payment.DoesNotExist:
            # logger.warning("Webhook for unknown payment %s", tran_id)
            return Response({"detail": "payment not found"}, status=404)

        # Idempotent handling: if already success, ignore
        if payment.status == Payment.STATUS_SUCCESS:
            return Response({"detail": "already processed"}, status=200)

        # SSLCommerz indicates 'VALID' for success in IPN, sometimes 'FAILED' otherwise
        if status_received in ('VALID', 'SUCCESS'):
            payment.status = Payment.STATUS_SUCCESS
            payment.transaction_id = info.get('val_id') or data.get('tran_id') or ''
            payment.save()

            # authorize device and add IMEI
            device = payment.device
            device.is_authorized = True
            device.save()
            if device.imei:
                AuthorizedIMEI.objects.get_or_create(imei=device.imei)

            print("payment confirmed, device authorized status done")

            return Response({"detail": "payment confirmed, device authorized"}, status=200)

        else:
            payment.status = Payment.STATUS_FAILED
            payment.transaction_id = info.get('val_id') or data.get('tran_id') or ''
            payment.save()
            return Response({"detail": "payment failed"}, status=200)




class PaymentSuccessView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
        return Response({"detail": "payment successful"}, status=200)

class PaymentFailView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
        return Response({"detail": "payment failed"}, status=200)

class PaymentCancelView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
        return Response({"detail": "payment canceled"}, status=200)



class PaymentsListView(generics.ListAPIView):
    """
    Admins and Staff can view all payments.
    User can view their payments
    Added filtering by status, user, or device.
    """
    serializer_class = PaymentDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            queryset = Payment.objects.select_related('user', 'device').all()
        else:
            queryset = Payment.objects.select_related('user', 'device').filter(user=user)  # regular users can see only their payments

        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        device_id = self.request.query_params.get('device_id')
        if device_id:
            queryset = queryset.filter(device_id=device_id)
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset
