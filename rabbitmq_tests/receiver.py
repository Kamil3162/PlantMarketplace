import pika
import json
import time
import os
import asyncio


def connect_to_rabbitmq():
    print("")
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


def process_message(ch, method, properties, body):
    try:
        message = json.loads(body)
        print(f"\n=== Received Message ===")
        print(f"Message ID: {message['message_id']}")
        print(f"Timestamp: {message['timestamp']}")
        print(f"Content: {message['content']}")
        print("======================\n")

        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except json.JSONDecodeError:
        print("Error: Could not decode message")
        ch.basic_nack(delivery_tag=method.delivery_tag)


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

    # Set up consumer
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue='test_queue',
        on_message_callback=process_message
    )

    print(' [*] Waiting for messages. To exit press CTRL+C')

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Shutting down receiver...")
    finally:
        connection.close()


if __name__ == '__main__':
    main()