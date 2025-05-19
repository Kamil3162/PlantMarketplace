from .celery_worker import ops_celery
import redis
import json
import ssl
from email.message import EmailMessage
import smtplib

result = ops_celery.send_products_email()

print(f"Zadanie zostało dodane do kolejki. ID zadania: {result['task_id']}")