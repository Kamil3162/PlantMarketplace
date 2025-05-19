# email_service/management/commands/start_email_consumer.py
import time

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Starts the RabbitMQ email consumer'

    def handle(self, *args, **options):
        from consumer import EmailConsumer

        self.stdout.write(self.style.SUCCESS('Starting email consumer...'))

        consumer = EmailConsumer()
        try:
            consumer.start_consuming()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Stopping consumer...'))