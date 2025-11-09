# ALX Travel App 0x03 - Celery & RabbitMQ Integration

## Overview
Django application with Celery and RabbitMQ for asynchronous email notifications on booking confirmations.

## Features
- Celery configured with RabbitMQ message broker
- Asynchronous booking confirmation emails
- Background task processing

## Prerequisites
- Python 3.8+
- Django 3.2+
- RabbitMQ
- Celery 5.0+

## Installation

```bash
# Install dependencies
pip install celery django-celery-results librabbitmq

# Install RabbitMQ
# Ubuntu/Debian
sudo apt-get install rabbitmq-server
sudo systemctl start rabbitmq-server

# macOS
brew install rabbitmq
brew services start rabbitmq
```

## Project Structure
```
alx_travel_app_0x03/
├── alx_travel_app_0x03/
│   ├── __init__.py          # Loads Celery app
│   ├── celery.py            # Celery configuration
│   ├── settings.py          # Celery + Email settings
│   └── ...
├── listings/
│   ├── tasks.py             # Email task
│   ├── views.py             # Triggers email on booking
│   └── ...
└── manage.py
```

## Configuration

### settings.py
```python
# Celery
CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-password'
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
```

## Running the Application

```bash
# Terminal 1: Start Celery Worker
celery -A alx_travel_app_0x03 worker --loglevel=info

# Terminal 2: Start Django Server
python manage.py runserver
```

## Testing

### Create a booking via API:
```bash
curl -X POST http://localhost:8000/api/bookings/ \
  -H "Content-Type: application/json" \
  -d '{
    "user": 1,
    "listing": 1,
    "check_in": "2024-12-01",
    "check_out": "2024-12-05"
  }'
```

### Check Celery logs for task execution:
```
[INFO] Task listings.send_booking_confirmation_email received
[INFO] Task listings.send_booking_confirmation_email succeeded
```

## Key Files

**celery.py**
```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_travel_app_0x03.settings')
app = Celery('alx_travel_app_0x03')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

**listings/tasks.py**
```python
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_booking_confirmation_email(booking_id, user_email, listing_title, check_in, check_out):
    send_mail(
        subject=f'Booking Confirmation - {listing_title}',
        message=f'Booking #{booking_id} confirmed from {check_in} to {check_out}',
        from_email='noreply@example.com',
        recipient_list=[user_email],
    )
```

**listings/views.py**
```python
from .tasks import send_booking_confirmation_email

class BookingViewSet(viewsets.ModelViewSet):
    def create(self, request, *args, **kwargs):
        # ... create booking ...
        send_booking_confirmation_email.delay(
            booking.id, booking.user.email, 
            booking.listing.title, 
            str(booking.check_in), 
            str(booking.check_out)
        )
        # ... return response ...
```

## Monitoring
- RabbitMQ UI: `http://localhost:15672` (guest/guest)
- Enable: `sudo rabbitmq-plugins enable rabbitmq_management`
