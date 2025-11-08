from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, BookingViewSet, InitiatePaymentAPIView, VerifyPaymentAPIView

router = DefaultRouter()
router.register(r'listings', ListingViewSet)
router.register(r'bookings', BookingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('payments/initiate/', InitiatePaymentAPIView.as_view(), name='payment-initiate'),
    path('payments/verify/', VerifyPaymentAPIView.as_view(), name='payment-verify'),
]