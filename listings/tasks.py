from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_booking_confirmation_email(email, booking_id):
    subject = "Booking Confirmation"
    message = f"Dear Customer,\n\nYour booking (ID: {booking_id}) has been confirmed.\nThank you for choosing ALX Travel!"
    sender = "noreply@travelapp.com"

    send_mail(subject, message, sender, [email])
    print(f"Confirmation email sent to {email} for booking {booking_id}")
