import os
import json
import time
import pika
from pika.exceptions import AMQPConnectionError
import logging

logger = logging.getLogger(__name__)

class EmailProducer(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(EmailProducer, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange_name = 'email_service'
        self.queue_name = 'emails1'
        self.routing_key = 'email_service'
        self.connect()

    def connect(self):
        """Establish connection to RabbitMQ"""
        tries = 5
        current_try = 0
        while current_try < tries:
            try:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=os.getenv('RABBITMQ_HOST', 'rabbitmq'),
                        port=int(os.getenv('RABBITMQ_PORT', '5672')),
                        credentials=pika.PlainCredentials(
                            username=os.getenv('RABBITMQ_DEFAULT_USER', 'myuser'),
                            password=os.getenv('RABBITMQ_DEFAULT_PASS', 'mypassword')
                        ),
                        heartbeat=600,
                        blocked_connection_timeout=300
                    )
                )
                self.channel = self.connection.channel()

                # Declare the exchange
                self.channel.exchange_declare(
                    exchange=self.exchange_name,
                    exchange_type='direct',
                    durable=True,
                    auto_delete=False
                )

                # Declare the queue
                self.channel.queue_declare(
                    queue=self.queue_name,
                    durable=True
                )

                # Bind the queue to the exchange
                self.channel.queue_bind(
                    queue=self.queue_name,
                    exchange=self.exchange_name,
                    routing_key=self.routing_key
                )

                logger.info(f"Connected to RabbitMQ and set up queue '{self.queue_name}'")

            except AMQPConnectionError as e:
                logger.error(f"Connection error: {e}")
                pass
            finally:
                time.sleep(5)
                current_try += 1

    def add_email_to_queue(self, email_data):
        """
        Add an email to the RabbitMQ queue

        Args:
            email_data (dict): Contains email details like:
                - receiver: Email recipient
                - subject: Email subject
                - body_html: HTML content (optional)
                - body_text: Plain text content

        Returns:
            bool: True if message was published successfully, False otherwise
        """
        try:
            # Ensure we have a connection
            if not self.connection or not self.connection.is_open:
                logger.warning("Connection closed, reconnecting...")
                self.connect()

            message = {
                'task' : 'send_email',
                'id': '123',
                'args': [],
                'kwargs': {
                    'sender' :'kamilholb@gmail.com',
                    'receiver' : email_data.get('to_email', 'kamilholb@gmail.com'),
                    'subject' : email_data.get('subject', 'subject'),
                }
            }

            # Convert the email data to JSON
            message_body = json.dumps(message)

            # Set message properties
            properties = pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
                content_type='application/json',
                timestamp=int(time.time())
            )

            # Publish the message
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=self.routing_key,
                body=message_body,
                properties=properties
            )

            logger.info(f"Email to {email_data.get('receiver')} added to queue")
            return True

        except Exception as e:
            logger.error(f"Error adding email to queue: {e}")
            return False

    def close_connection(self):
        """Close the connection to RabbitMQ"""
        if self.connection and self.connection.is_open:
            self.connection.close()
            logger.info("RabbitMQ connection closed")


EmailProducerInstance = EmailProducer()

