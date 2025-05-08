import threading
import pika
import os
import json
import sys
import time


class RabbitMQConnection:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=os.getenv('RABBITMQ_HOST', 'localhost'),
                    port=int(os.getenv('RABBITMQ_PORT', '5672')),
                    credentials=pika.PlainCredentials(
                        username='myuser',
                        password='mypassword',
                    ),
                    heartbeat=600,  # Keep connection alive
                    blocked_connection_timeout=300
                )
            )

            self.channel = self.connection.channel()
            self.channel.queue_declare(queue='products', durable=True)

            print("Successfully connected to RabbitMQ")

        except pika.exceptions.AMQPConnectionError as e:
            print(f"Failed to connect to RabbitMQ: {e}")
            time.sleep(5)  # Wait before retry
            self.connect()  # Recursive retry

    def close(self):
        if self.connection and self.connection.is_open:
            self.connection.close()
            print("RabbitMQ connection closed")


class ProductConsumer(RabbitMQConnection):
    def start_consuming(self):
        # Set prefetch count to limit the number of unacknowledged messages
        self.channel.basic_qos(prefetch_count=1)

        # Don't use auto_ack=True in production
        self.channel.basic_consume(
            queue='products',
            on_message_callback=self.callback,
            auto_ack=False
        )

        print(' [*] Waiting for messages. To exit press CTRL+C')
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
            self.close()
        except pika.exceptions.ConnectionClosedByBroker:
            # Reconnect if broker closed connection
            print("Connection closed by broker, reconnecting...")
            self.connect()
            self.start_consuming()
        except Exception as e:
            print(f"Unexpected error: {e}")
            self.close()

    def callback(self, channel, method, properties, body):
        try:
            # Parse the JSON message
            message = json.loads(body)
            description = message.get('description', '')

            print(f"Received message: {description}")

            # Process the message (add your business logic here)
            # ...

            # Acknowledge the message only after successful processing
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except json.JSONDecodeError:
            print("Failed to decode JSON message")
            # Reject the message but don't requeue if it's malformed
            channel.basic_reject(delivery_tag=method.delivery_tag,
                                 requeue=False)
        except Exception as e:
            print(f"Error processing message: {e}")
            # Reject and requeue on processing errors
            channel.basic_reject(delivery_tag=method.delivery_tag,
                                 requeue=True)


class ProductProducer(RabbitMQConnection):
    def send_message(self, description):
        try:
            # First check if description is None or empty
            if description is None:
                print("Cannot send None as a message")
                return False

            message = {
                'description': description,
                'timestamp': time.time()
            }

            # Explicitly check the JSON serialization
            message_body = json.dumps(message)
            if not message_body:
                print("JSON serialization resulted in empty message")
                return False

            # Check if connection is still valid
            if not self.connection or not self.connection.is_open:
                print("Connection lost, attempting to reconnect...")
                self.connect()

            # Check if channel is still valid
            if not self.channel or not self.channel.is_open:
                print("Channel closed, creating a new one...")
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue='products', durable=True)

            self.channel.basic_publish(
                exchange='',
                routing_key='products',
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
            print(f"Sent message: {description}")
            return True
        except pika.exceptions.AMQPConnectionError:
            print("Connection lost, attempting to reconnect...")
            self.connect()
            return self.send_message(description)  # Retry after reconnection
        except Exception as e:
            print(f"Failed to send message: {e}")
            return False


class ThreadConsumer(threading.Thread):
    def __init__(self, RabbitMQConnection):
        self.connection = RabbitMQConnection


def run_consumer():
    consumer = ProductConsumer()
    try:
        consumer.start_consuming()
    finally:
        consumer.close()


def run_producer():
    producer = ProductProducer()
    try:
        while True:
            value = input("Enter message (or 'exit' to quit): ")
            if value.lower() == 'exit':
                break
            producer.send_message(description=value)
    except KeyboardInterrupt:
        print("Producer stopped by user")
    finally:
        producer.close()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'produce':
        run_producer()
    else:
        run_consumer()