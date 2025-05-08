import os
import pika
import json
import sys
import time
from pika.exceptions import AMQPConnectionError


class ConsumerRabbitMQ:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange_name = 'product_messages'
        self.queue_name = 'products'
        self.routing_key = 'product_updates'
        self.connect()

    def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=os.getenv('RABBITMQ_HOST', 'localhost'),
                    port=int(os.getenv('RABBITMQ_PORT', '5672')),
                    credentials=pika.PlainCredentials(
                        username=os.getenv('RABBITMQ_DEFAULT_USER', 'myuser'),
                        password=os.getenv('RABBITMQ_DEFAULT_PASS',
                                           'mypassword')
                    ),
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
            )
            self.channel = self.connection.channel()

            # Declare the same exchange as in producer
            self.channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type='direct',
                durable=True,
                auto_delete=False
            )

            # Declare the same queue as in producer
            self.channel.queue_declare(
                queue=self.queue_name,
                durable=True
            )

            # Bind with the same routing key
            self.channel.queue_bind(
                queue=self.queue_name,
                exchange=self.exchange_name,
                routing_key=self.routing_key
            )

            print(
                f"Connected to RabbitMQ and bound to queue '{self.queue_name}'")

        except AMQPConnectionError as e:
            print(f"Connection error: {e}")
            time.sleep(5)
            self.connect()

    def process_message(self, ch, method, properties, body):
        """Process a message from the queue"""
        try:
            # Parse the JSON message
            message = json.loads(body)
            print(f"\nReceived message: {message}")

            # Add your message processing logic here
            # For example:
            print(f"Processing message with ID: {message.get('id')}")
            print(f"Message body: {message.get('body')}")

            # Simulate processing time
            time.sleep(1)

            # Acknowledge the message once processed
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print("Message processing complete")

        except Exception as e:
            print(f"Error processing message: {e}")
            # Negative acknowledgment - requeue the message
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start_consuming(self):
        """Start consuming messages from the queue"""
        # Set quality of service - only process one message at a time
        self.channel.basic_qos(prefetch_count=1)

        # Start consuming from the queue
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.process_message
        )

        print(
            f"Waiting for messages on queue '{self.queue_name}'. To exit press CTRL+C")
        try:
            # Start consuming indefinitely
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print("\nConsumer stopped by user")
            self.channel.stop_consuming()
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            self.close_connection()

    def close_connection(self):
        """Close the connection to RabbitMQ"""
        if self.connection and self.connection.is_open:
            self.connection.close()
            print("Connection closed")


if __name__ == '__main__':
    consumer = ConsumerRabbitMQ()
    consumer.start_consuming()