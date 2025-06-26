# # email_service/management/commands/start_email_consumer.py
#
# from django.authenticate.management.base import BaseCommand
#
# from ...producer import EmailProducer
#
#
# class Command(BaseCommand):
#     help = 'Starts the RabbitMQ email consumer'
#
#     def handle(self, *args, **options):
#         self.stdout.write(self.style.SUCCESS('Starting email consumer...'))
#
#         producer = EmailProducer()
#
#         try:
#             consumer.()
#         except KeyboardInterrupt:
#             self.stdout.write(self.style.WARNING('Stopping consumer...'))