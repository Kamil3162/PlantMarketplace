import json
import uuid

import pika
from pika import exceptions
from django.utils import timezone

from .config import RabbitMQConfig

class ProducerQueue:
    __extenstion = 'json'
    __task_name = 'set_auth_user_data'
    __task_id = None

    def __init__(self):
        self.config = RabbitMQConfig()
        self.rabbit_connection = pika.BlockingConnection(
            parameters=pika.ConnectionParameters(
                host=self.config.host,
                port=self.config.port,
                credentials=pika.PlainCredentials(
                    username=self.config.username,
                    password=self.config.password
                )
            )
        )

        self.__connection_init()

    def __connection_init(self):
        self.channel = self.rabbit_connection.channel()

        self.channel.exchange_declare(
            exchange=self.config.exachage_name,
            exchange_type='direct',
            durable=True,
            auto_delete=True
        )

        self.channel.queue_declare(
            queue=self.config.queue_name,
            durable=True
        )

        self.channel.queue_bind(
            queue=self.config.queue_name,
            exchange=self.config.exachage_name,
            routing_key=self.config.routing_key
        )

    # during login for example
    def prepare_data(self, informations: dict):
        """
            Prepare data format to send into celery worker api gateway into store crucial informations inside redis
            This operations will help me to speed up entire project implementation
        Args:
            informations: dict | payload
        Returns:

        """
        try:
            if not isinstance(informations, dict):
                raise TypeError(f"Wrong data format target: dict input-{informations.__class__}")

            user_payload = dict()
            user_payload['user_id'] = informations.get('user_id')
            user_payload['jti'] = informations.get('jti')
            user_payload['exp'] = informations.get('exp')
            user_payload['data_created'] = str(timezone.now())

            return user_payload
        except TypeError as exc:
            print(exc)

    def prepare_celery_format(self, celery_args: list = [], celery_body: dict=None):
        task_name = ProducerQueue.__task_name
        if not celery_body:
            celery_body = {}

        celery_task = {
            'task': task_name,
            'id': str(uuid.uuid4()),
            'args': celery_args,
            'kwargs': celery_body
        }

        return json.dumps(celery_task)

    def publish_data(self, body: dict):
        prepared_data = self.prepare_data(body)
        task = self.prepare_celery_format(celery_body=prepared_data)

        try:
            self.channel.basic_publish(
                exchange=self.config.queue_name,
                routing_key=self.config.queue_name,
                body=task,
                properties=pika.BasicProperties(
                    headers={
                    'id': str(uuid.uuid4()),
                    'task':ProducerQueue.__task_name,
                    },
                    content_type='application/json'
                )
            )
        except exceptions.UnroutableError as exc:
            print(exc)

    def close(self):
        import sys
        self.rabbit_connection.close()
        print("Connection closed")


rabbit_producer = ProducerQueue()