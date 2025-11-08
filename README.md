
# 🧾 Integration of Chapa API for Payment Processing in Django

## 🎯 Objective

This project integrates the **Chapa Payment API** into a Django travel booking application to allow users to make secure online payments for their bookings.
It handles payment initiation, verification, and automatic status updates after successful or failed transactions.

---

## 🧱 Project Details

**Repository:** `alx_travel_app_0x02`
**Directory:** `alx_travel_app`
**Main Files:**

* `listings/models.py`
* `listings/views.py`
* `listings/urls.py`
* `README.md`

This project was duplicated from **alx_travel_app_0x01** and enhanced with payment integration features.

---

## 🔑 Step 1: Chapa API Setup

1. Created a Chapa Developer Account → [https://developer.chapa.co](https://developer.chapa.co)

2. Obtained **API keys** from the dashboard.

3. Stored the secret key securely in an environment variable:

   ```bash
   export CHAPA_SECRET_KEY="sk_test_your_chapa_secret_key"
   ```

4. Added this line to `settings.py` to access it:

   ```python
   import os
   CHAPA_SECRET_KEY = os.environ.get("CHAPA_SECRET_KEY")
   ```

---

## 💳 Step 2: Payment Model

Added a `Payment` model to `listings/models.py` to store transaction details.

```python
class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey('Booking', on_delete=models.SET_NULL, related_name='payments', null=True, blank=True)
    tx_ref = models.CharField(max_length=200, unique=True)
    chapa_reference = models.CharField(max_length=200, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='ETB')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### ✅ What I Learned

* How to connect payments to bookings with foreign keys.
* How to track payment lifecycle using status fields.
* How to safely store third-party API responses in JSON fields.

---

## 🌐 Step 3: Payment API Views

Implemented two main API endpoints in `listings/views.py`:

### 1. Initiate Payment

* Accepts a booking ID.
* Sends POST request to **Chapa’s `/transaction/initialize`** endpoint.
* Receives a `checkout_url` for the user to complete payment.
* Saves transaction reference and metadata in the database.

### 2. Verify Payment

* Accepts a transaction reference (`tx_ref`).
* Sends GET request to **`/transaction/verify/{tx_ref}`**.
* Updates the payment status as “Completed” or “Failed” based on response.

### Endpoints

```
POST  /listings/payments/initiate/
GET   /listings/payments/verify/?tx_ref=<reference>
```

---

## ⚙️ Step 4: Payment Workflow

1. User creates a booking.
2. The system initiates a payment request to Chapa.
3. Chapa returns a **checkout URL** for the user.
4. After payment, verification confirms the status.
5. Payment status updates in the `Payment` model.
6. (Optional) A confirmation email is sent using Celery.

---

## 🧪 Step 5: Testing in Chapa Sandbox

Chapa’s **sandbox environment** was used for safe testing.

### 🔹 Initiate Payment Example

```bash
curl -X POST http://127.0.0.1:8000/listings/payments/initiate/ \
 -H "Content-Type: application/json" \
 -d '{"booking_id": "your-booking-id"}'
```

**Expected Response**

```json
{
  "checkout_url": "https://checkout.chapa.co/tx/xyz...",
  "tx_ref": "booking-12345"
}
```

### 🔹 Verify Payment Example

```bash
curl http://127.0.0.1:8000/listings/payments/verify/?tx_ref=booking-12345
```

**Expected Response**

```json
{
  "payment_status": "completed",
  "chapa_data": {...}
}
```

---

## 🧰 Step 6: Seeding Test Data

A `seed.py` script was created to populate 50 users, listings, bookings, reviews, and payments.
This allows easy testing of the Chapa payment flow.

```bash
python seed.py
```

Each payment links to a booking, ensuring realistic relationships for testing.


## 🧠 What I Learned

* How to integrate **third-party APIs** into Django apps.
* How to handle **secure payments** using **environment variables**.
* How to use **requests library** to communicate with REST APIs.
* How to **verify transactions** and update models dynamically.
* How to **seed databases** for development and testing.

---

## 📸 Screenshots (for Manual Review)

Below are placeholders for submission (replace with your actual images):

* ✅ Payment initiation success log
* ✅ Chapa checkout page (sandbox)
* ✅ Payment verification success log
* ✅ Payment model status updated to “Completed”

---

## 🗂 Repository Structure

```
alx_travel_app_0x02/
│
├── alx_travel_app/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── listings/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── serializers.py
│   └── tasks.py
│
├── seed.py
└── README.md
```

---

## 🏁 Conclusion

This project successfully demonstrates how to **integrate and verify payments** using the **Chapa API** in a Django application.
It provides a secure, testable, and production-ready workflow for online payment processing.
