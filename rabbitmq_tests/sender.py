import pika
import json
import time
import os
from datetime import datetime

def connect_to_rabbitmq():
    retries = 5
    while retries > 0:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host='rabbitmq',
                    port=5672,
                    credentials=pika.PlainCredentials(
                        username='myuser',
                        password='mypassword'
                    )
                )
            )
            return connection
        except pika.exceptions.AMQPConnectionError:
            print(f"Failed to connect, retrying... ({retries} attempts left)")
            retries -= 1
            time.sleep(5)
    raise Exception("Could not connect to RabbitMQ")


def main():
    # Wait for RabbitMQ to be ready
    print("Waiting for RabbitMQ to be ready...")
    time.sleep(2)

    connection = connect_to_rabbitmq()
    channel = connection.channel()

    # Declare the exchange and queue
    channel.exchange_declare(exchange='test_exchange', exchange_type='direct')
    channel.queue_declare(queue='test_queue')
    channel.queue_bind(exchange='test_exchange', queue='test_queue',
                       routing_key='test_key')

    message_count = 0

    try:
        while True:
            message_count += 1
            message = {
                'message_id': message_count,
                'timestamp': datetime.now().isoformat(),
                'content': f'Test message #{message_count}'
            }

            channel.basic_publish(
                exchange='test_exchange',
                routing_key='test_key',
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2  # Make message persistent
                )
            )

            print(f" [x] Sent message #{message_count}")
            time.sleep(1)  # Send a message every 5 seconds

    except KeyboardInterrupt:
        print("Shutting down sender...")
    finally:
        connection.close()

if __name__ == '__main__':
    main()