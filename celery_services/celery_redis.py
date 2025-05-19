import smtplib
import os.path
import ssl
import sys

import celery
from email.message import EmailMessage
import redis
import json

from .config import ConfigCelery, EmailConfig
from redis_microservices import redis_product_client

class CeleryOperations:
    def __init__(self, config:ConfigCelery):
        self.app = celery.Celery(
            config.name,
            broker=config.redis_broker,
            # backend=config.result_backend
        )
        self._email_config = EmailConfig()

        self.app.conf.update(
            timezone=config.timezone,
            enable_utc=config.enable_utc
        )
        self.register_tasks()

    def register_tasks(self):
        """Rejestruje zadania Celery"""
        @self.app.task(name='fetch_and_email_products')
        def fetch_and_email_products(recipient=None, subject=None):
            """Pobiera wszystkie produkty z Redisa i wysyła email"""
            # Domyślne wartości
            if not recipient:
                recipient = self._email_config.email_receiver
            if not subject:
                subject = "Lista produktów z Redisa"

            # Pobierz dane z Redisa
            products = self.get_products_from_redis()
            if products:
                body = 'test'
            else:
                body = 'brak produktów'
            # Formatuj treść emaila
            body = self._format_products_for_email(products)

            # Utwórz i wyślij email
            email_data = {
                "sender": self._email_config.email_sender,
                "receiver": recipient,
                "subject": subject,
                "body": body
            }

            success = self._send_email(email_data)

            return {
                "success": success,
                "products_count": len(products),
                "recipient": recipient
            }

    def get_products_from_redis(self):
        """Pobiera wszystkie produkty z Redisa"""
        redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )

        # Pobierz wszystkie klucze produktów (zakładając prefix 'product:')
        product_keys = redis_client.keys('product:*')
        products = []

        for key in product_keys:
            product_data = redis_client.hgetall(key)
            if product_data:
                try:
                    products.append(product_data)
                except json.JSONDecodeError:
                    # Ignoruj nieprawidłowe dane
                    pass

        return products

    def _format_products_for_email(self, products):
        """Formatuje produkty do treści emaila"""
        if not products:
            return "Brak produktów w bazie danych."

        body = "Lista produktów:\n\n"

        for i, product in enumerate(products):
            body += f"Produkt #{i}\n"
            body += f"ID: {product.get('id', 'N/A')}\n"
            body += f"Nazwa: {product.get('name', 'N/A')}\n"
            body += f"Cena: {product.get('price', 'N/A')}\n"

            if 'description' in product:
                body += f"Opis: {product.get('description')}\n"

            body += "\n"

        return body


    def create_email(self, sender, receiver, subject, body):
        """Tworzy obiekt EmailMessage"""
        email_obj = EmailMessage()
        email_obj['From'] = sender
        email_obj['To'] = receiver
        email_obj['Subject'] = subject
        email_obj.set_content(body)
        return email_obj

    def _send_email(self, email_data):
        """Wysyła email używając SMTP"""
        try:
            # Utworzenie obiektu email
            email_obj = self.create_email(
                sender=email_data['sender'],
                receiver=email_data['receiver'],
                subject=email_data['subject'],
                body=email_data['body']
            )

            # Konfiguracja SSL
            context = ssl.create_default_context()

            # Wysyłka emaila
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(email_data['sender'], self._email_config.email_password)
                smtp.send_message(email_obj)

            return True
        except Exception as e:
            print(f"Błąd wysyłania emaila: {e}")
            return False

    def send_products_email(self, recipient=None, subject=None):
        print('send products email - exec')
        """Wywołuje zadanie asynchronicznie"""
        # Używamy .delay() do asynchronicznego wywołania zadania
        task = self.app.send_task(
            'fetch_and_email_products',
            kwargs={
                'recipient': recipient,
                'subject': subject
            }
        )

        return {
            'task_id': task.id,
            'status': 'Zadanie zostało dodane do kolejki'
        }



