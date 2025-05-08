import os
import time
import pika
import json
import sys
import uuid
from pika.exceptions import AMQPConnectionError


class RabbitMQProducer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange_name = 'product_messages'
        self.queue_name = 'products'
        self.routing_key = 'product_updates'
        self.create_connection()

    def create_connection(self):
        try:
            # Use environment variables with defaults
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=os.getenv('RABBITMQ_HOST', 'localhost'),
                    port=int(os.getenv('RABBITMQ_PORT', '5672')),
                    credentials=pika.PlainCredentials(
                        username=os.getenv('RABBITMQ_DEFAULT_USER', 'myuser'),
                        password=os.getenv('RABBITMQ_DEFAULT_PASS',
                                           'mypassword'),
                    ),
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
            )
            self.channel = self.connection.channel()

            # Declare exchange - setting auto_delete=False is safer for production
            self.channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type='direct',
                durable=True,
                auto_delete=False,
            )

            # Declare queue
            self.channel.queue_declare(
                queue=self.queue_name,
                durable=True
            )

            # Bind queue to exchange with routing key
            self.channel.queue_bind(
                queue=self.queue_name,
                exchange=self.exchange_name,
                routing_key=self.routing_key,
            )

            print(
                f"Connected to RabbitMQ and created exchange '{self.exchange_name}' and queue '{self.queue_name}'")

        except AMQPConnectionError as e:
            print(f"Connection error: {e}")
            # Wait before retry
            time.sleep(5)
            # Retry connection
            self.create_connection()

    def send_message(self, body):
        """Send a message to the RabbitMQ queue"""
        if not self.connection or self.connection.is_closed:
            print("Connection is closed, reconnecting...")
            self.create_connection()

        try:
            # Create message with UUID
            message = {
                'id': str(uuid.uuid4()),
                'timestamp': time.time(),
                'body': body,
            }

            message_json = json.dumps(message)

            # Publish the message
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=self.routing_key,
                body=message_json,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )
            print(f"Message sent: {message}")
            return True

        except Exception as e:
            print(f"Error sending message: {e}")
            # Try to reconnect
            self.create_connection()
            return False

    def close_connection(self):
        """Close the connection to RabbitMQ"""
        if self.connection and self.connection.is_open:
            self.connection.close()
            print("Connection closed")


if __name__ == '__main__':
    producer = RabbitMQProducer()
    try:
        while True:
            message = input("Enter message (or 'exit' to quit): ")
            if message.lower() == 'exit':
                break
            producer.send_message(message)
    except KeyboardInterrupt:
        print("\nProducer stopped by user")
    finally:
        producer.close_connection()
        sys.exit(0)