"""
    Utils file have a bunch of function for manage User data model and
    making a various operations :
        - generate random users
"""
import random

from django.core.management.base import BaseCommand
from faker import Faker

from data.models import CustomUser

User = CustomUser
class Command(BaseCommand):
    def handle(self, *args, **options):
        fake = Faker()
        try:
            for i in range(5):
                User.objects.create_superuser(  # Use User.objects instead of user_manager
                    # username=fake.email(),
                    first_name=f"kamision{i}",
                    last_name=f"kamision{i}",
                    email=f"kamision{i}@gmail.com",
                    password="test"
                )
        except Exception as e:
            self.stdout.write(f"Error creating user: {e}")
            return

        self.stdout.write(self.style.SUCCESS("Successfully created admin users"))