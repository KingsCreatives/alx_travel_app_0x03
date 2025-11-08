import os
import django
import uuid
import random
from datetime import date, timedelta
from decimal import Decimal

# ----------------------------------------------------------------
# Setup Django environment
# ----------------------------------------------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_travel_app.settings")
django.setup()

from listings.models import User, Listing, Booking, Review, Payment

# ----------------------------------------------------------------
# 1. Optional: Clear existing data
# ----------------------------------------------------------------
print("🧹 Clearing existing data...")
Payment.objects.all().delete()
Review.objects.all().delete()
Booking.objects.all().delete()
Listing.objects.all().delete()
User.objects.all().delete()

# ----------------------------------------------------------------
# 2. Create Users (hosts and guests)
# ----------------------------------------------------------------
print("👤 Creating users...")
roles = ["guest", "host"]
users = []
for i in range(20):
    role = random.choice(roles)
    user = User.objects.create_user(
        id=uuid.uuid4(),
        username=f"user{i}",
        email=f"user{i}@example.com",
        first_name=f"First{i}",
        last_name=f"Last{i}",
        phone_number=f"+2335{random.randint(1000000,9999999)}",
        role=role,
        password="password123"
    )
    users.append(user)

hosts = [u for u in users if u.role == "host"]
guests = [u for u in users if u.role == "guest"]

print(f"✅ Created {len(hosts)} hosts and {len(guests)} guests")

# ----------------------------------------------------------------
# 3. Create Listings (each belongs to a host)
# ----------------------------------------------------------------
print("🏠 Creating listings...")
listings = []
for i in range(30):
    host = random.choice(hosts)
    listing = Listing.objects.create(
        id=uuid.uuid4(),
        host=host,
        name=f"Listing {i}",
        description=f"This is a test listing number {i}.",
        location=random.choice(["Accra", "Kumasi", "Tamale", "Cape Coast", "Takoradi"]),
        price_per_unit=Decimal(random.randint(100, 1000))
    )
    listings.append(listing)
print(f"✅ Created {len(listings)} listings")

# ----------------------------------------------------------------
# 4. Create Bookings (each belongs to a guest and listing)
# ----------------------------------------------------------------
print("📅 Creating bookings...")
bookings = []
for i in range(40):
    listing = random.choice(listings)
    guest = random.choice(guests)
    start_date = date.today() + timedelta(days=random.randint(1, 5))
    end_date = start_date + timedelta(days=random.randint(1, 5))
    total_price = Decimal(listing.price_per_unit) * Decimal((end_date - start_date).days)
    booking = Booking.objects.create(
        id=uuid.uuid4(),
        listing=listing,
        user=guest,
        start_date=start_date,
        end_date=end_date,
        total_price=total_price,
        status=random.choice(["pending", "confirmed", "canceled"])
    )
    bookings.append(booking)
print(f"✅ Created {len(bookings)} bookings")

# ----------------------------------------------------------------
# 5. Create Reviews (each guest reviews random listing)
# ----------------------------------------------------------------
print("💬 Creating reviews...")
for i in range(20):
    listing = random.choice(listings)
    reviewer = random.choice(guests)
    Review.objects.create(
        id=uuid.uuid4(),
        listing=listing,
        user=reviewer,
        rating=random.randint(1, 5),
        comment=f"Great stay at {listing.name}!"
    )
print("✅ Created 20 reviews")

# ----------------------------------------------------------------
# 6. Create Payments (linked to bookings)
# ----------------------------------------------------------------
print("💳 Creating payments...")
for i in range(40):
    booking = random.choice(bookings)
    tx_ref = f"seed-{uuid.uuid4().hex[:10]}"
    Payment.objects.create(
        id=uuid.uuid4(),
        booking=booking,
        tx_ref=tx_ref,
        chapa_reference=f"chapa-{uuid.uuid4().hex[:6]}",
        amount=booking.total_price,
        currency="ETB",
        status=random.choice(["pending", "completed", "failed"]),
        metadata={"source": "seed_script", "note": f"Payment {i}"}
    )
print("✅ Created 40 payments")

print("🎉 Database successfully seeded with sample data!")
