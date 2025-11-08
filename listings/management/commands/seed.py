import random
from django.core.management.base import BaseCommand
from django_seed import Seed
from listings.models import User, Listing, Review
from faker import Faker

class Command(BaseCommand):
    help = "Seeds the database with fake data"

    def handle(self, *args, **kwargs):
        fake = Faker()
        seeder = Seed.seeder()

        
        seeder.add_entity(User, 10, {  
            'id': lambda x: random.randint(1000, 10000),  
            'email': lambda x: fake.email(),  
            'phone_number': lambda x: fake.phone_number(),  
            'role': lambda x: random.choice(['guest', 'host', 'admin']),  
            'created_at': lambda x: fake.date_this_decade(),  
        })

       
        seeder.add_entity(Listing, 10, {  
            'host': lambda x: random.choice(User.objects.all()),  
            'name': lambda x: fake.company(),  
            'description': lambda x: fake.text(),  
            'location': lambda x: fake.city(),  
            'price_per_unit': lambda x: round(random.uniform(10.0, 500.0), 2),  
            'created_at': lambda x: fake.date_this_year(),  
            'updated_at': lambda x: fake.date_this_year(),  
        })

       
        seeder.add_entity(Review, 10, {  
            'listing': lambda x: random.choice(Listing.objects.all()),  
            'user': lambda x: random.choice(User.objects.all()),  
            'rating': lambda x: random.randint(1, 5),  
            'comment': lambda x: fake.text(),  
            'created_at': lambda x: fake.date_this_year(),  
        })

        
        seeder.execute()

        
        self.stdout.write(self.style.SUCCESS("Database successfully seeded with fake data"))
