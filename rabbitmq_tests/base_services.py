import os
import pika

class RabbitMQService:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='localhost',
                port=5672,
                credentials=pika.PlainCredentials(
                    os.getenv('RABBITMQ_DEFAULT_USER'),
                    os.getenv('RABBITMQ_DEFAULT_PASS'),
                )
            )
        )
        self.channel = self.connection.channel()
        self._setup_exchange()

    def _setup_exchange(self):
        self.channel.basic_publish(
            exchange='',
            routing_key='hello',
            body='Hello World!',
        )

    def _close_connection(self):
        self.connection.close()
