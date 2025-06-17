import os
import json
import time
import pika
import smtplib
import ssl
import logging
import celery

from pika.exceptions import AMQPConnectionError
from email.message import EmailMessage
from celery_conf import ConfigCelery
import dotenv

dotenv.load_dotenv()

logger = logging.getLogger(__name__)


class EmailConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange_name = 'email_service'
        self.queue_name = 'emails'
        self.routing_key = 'email_service'
        self.celery_worker = celery.Celery(
            str(f'email-{__file__}'),
            broker=ConfigCelery.broker_url
        )
        self.connect()

    def connect(self):
        """Establish connection to RabbitMQ"""
        max_retries = 30  # Zwiększamy liczbę prób
        retry = 0

        while retry < max_retries:
            try:
                print(f"Próba połączenia z RabbitMQ ({retry + 1}/{max_retries})...")
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=os.getenv('RABBITMQ_HOST', 'rabbitmq'),
                        port=int(os.getenv('RABBITMQ_PORT', '5672')),
                        credentials=pika.PlainCredentials(
                            username=os.getenv('RABBITMQ_DEFAULT_USER', 'myuser'),
                            password=os.getenv('RABBITMQ_DEFAULT_PASS', 'mypassword')
                        ),
                        heartbeat=600,
                        blocked_connection_timeout=300,
                        connection_attempts=3  # Dodajemy wewnętrzne próby
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
                return True  # Zwróć True, jeśli połączenie się powiodło

            except AMQPConnectionError as e:
                logger.error(f"Próba {retry + 1}/{max_retries}: Błąd połączenia z RabbitMQ: {e}")
                retry += 1
                if retry >= max_retries:
                    logger.error("Osiągnięto maksymalną liczbę prób połączenia z RabbitMQ")
                    return False
                time.sleep(5)  # Poczekaj 5 sekund przed kolejną próbą

        return False  # Zwróć False, jeśli wszystkie próby zawiodły

    def process_email(self, email_data):
        """Process and send an email"""
        try:
            # Create email message
            msg = EmailMessage()
            msg['From'] = email_data.get('sender', 'kamilholb@gmail.com')
            msg['To'] = email_data.get('receiver', 'kamilholb@gmail.com')
            msg['Subject'] = email_data.get('subject', 'test message')

            # Set content
            if 'body_html' in email_data and email_data['body_html']:
                msg.add_alternative(email_data['body_html'], subtype='html')
            msg.set_content(email_data.get('body_text', ''))

            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
                server.login(
                    'kamilholb@gmail.com',
                    '#### #### ####'
                )

                server.send_message(msg)

            logger.info(f"Email sent to {email_data.get('receiver')}")
            return True
        except Exception as e:
            logger.error(f"Failed to process email: {e}")
            return False

    def callback(self, ch, method, properties, body):
        """Callback function for message processing"""
        try:
            # Parse message
            print(body)
            email_data = json.loads(body)

            # Process email
            success = self.process_email(email_data)

            if success:
                # Acknowledge message
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.info("Message acknowledged")
            else:
                # Negative acknowledgment - requeue
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                logger.warning("Message not acknowledged, will be requeued")

        except json.JSONDecodeError:
            logger.error("Invalid JSON in message")
            # Reject message without requeuing
            ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error(f"Error in callback: {e}")
            # Reject message, requeue it
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start_consuming(self):
        """Start consuming messages from the queue"""
        max_retries = 5
        retry = 0

        while retry < max_retries:
            try:
                # Sprawdź czy połączenie istnieje i jest otwarte
                if not self.connection or not self.connection.is_open:
                    logger.info("Brak połączenia z RabbitMQ, próba ponownego połączenia...")
                    if not self.connect():
                        logger.error("Nie można połączyć się z RabbitMQ. Próba ponowna za 5 sekund.")
                        time.sleep(5)
                        retry += 1
                        continue

                # Set QoS - only get one message at a time
                self.channel.basic_qos(prefetch_count=1)

                # Start consuming
                self.channel.basic_consume(
                    queue=self.queue_name,
                    on_message_callback=self.callback
                )

                logger.info(f"Rozpoczęto konsumpcję z kolejki '{self.queue_name}'")
                self.channel.start_consuming()

            except KeyboardInterrupt:
                logger.info("Zatrzymano konsumenta (przerwanie klawiaturą)")
                if self.connection and self.connection.is_open:
                    self.channel.stop_consuming()
                    self.connection.close()
                break

            except Exception as e:
                logger.error(f"Błąd podczas konsumpcji: {e}")
                retry += 1
                if retry >= max_retries:
                    logger.error("Osiągnięto maksymalną liczbę prób. Zatrzymywanie konsumenta.")
                    break

                logger.info(f"Ponowna próba za 5 sekund... ({retry}/{max_retries})")
                time.sleep(5)

                # Zamknij połączenie, jeśli nadal jest otwarte
                if self.connection and self.connection.is_open:
                    try:
                        self.connection.close()
                    except:
                        pass


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Start consumer
    consumer = EmailConsumer()
    consumer.start_consuming()