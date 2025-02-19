"""
    Utils file have a bunch of function for manage User data model and
    making a various operations :
        - generate random users
"""
import random

from django.core.management.base import BaseCommand
from faker import Faker

from account.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        fake = Faker()
        try:
            for _ in range(100):
                User.objects.create_user(  # Use User.objects instead of user_manager
                    # username=fake.email(),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    email=fake.email(),
                    password="test"
                )
        except Exception as e:
            self.stdout.write(f"Error creating user: {e}")
            return

        self.stdout.write(self.style.SUCCESS("Successfully created users"))

