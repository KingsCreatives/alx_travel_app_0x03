import os
import uuid
import requests
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings
from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer, PaymentSerializer
from .tasks import send_booking_confirmation_email


CHAPA_INIT_URL = "https://api.chapa.co/v1/transaction/initialize"
CHAPA_VERIFY_URL = "https://api.chapa.co/v1/transaction/verify/{}"

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def perform_create(self, serializer):
        booking = serializer.save()
        send_booking_confirmation_email.delay(booking.user.email, booking.id)

def get_headers():
    secret = os.environ.get('CHAPA_TEST_SECRET_KEY') or getattr(settings, 'CHAPA_TEST_SECRET_KEY', None)
    return {"Authorization": f"Bearer {secret}", "Content-Type": "application/json"}


class InitiatePaymentAPIView(APIView):
    def post(self, request):
        booking_id = request.data.get('booking_id')
        if not booking_id:
            return Response({"error": "booking_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)

        tx_ref = f"booking-{uuid.uuid4().hex[:8]}"
        payment = Payment.objects.create(
            booking=booking,
            tx_ref=tx_ref,
            amount=booking.total_price,
            status='pending'
        )

        payload = {
            "amount": str(payment.amount),
            "currency": "ETB",
            "email": booking.user.email,
            "first_name": booking.user.first_name,
            "last_name": booking.user.last_name,
            "tx_ref": tx_ref,
            "callback_url": request.data.get("callback_url", ""),
        }

        try:
            response = requests.post(CHAPA_INIT_URL, json=payload, headers=get_headers())
            data = response.json()
            payment.metadata = data
            payment.save()

            checkout_url = data.get('data', {}).get('checkout_url', None)
            return Response({"checkout_url": checkout_url, "tx_ref": tx_ref}, status=201)
        except Exception as e:
            payment.status = 'failed'
            payment.metadata = {"error": str(e)}
            payment.save()
            return Response({"error": str(e)}, status=500)

class VerifyPaymentAPIView(APIView):
    def get(self, request):
        tx_ref = request.query_params.get('tx_ref')
        if not tx_ref:
            return Response({"error": "tx_ref required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = Payment.objects.get(tx_ref=tx_ref)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

        response = requests.get(CHAPA_VERIFY_URL.format(tx_ref), headers=get_headers())
        data = response.json()

        status_from_chapa = data.get('data', {}).get('status', '')
        if status_from_chapa == 'success':
            payment.status = 'completed'
        else:
            payment.status = 'failed'
        payment.metadata = data
        payment.save()

        return Response({"payment_status": payment.status, "chapa_data": data})
