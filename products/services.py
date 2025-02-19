import pika

class InventoryService:
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
        self.channel.basic_publish('hello')

        def callback(ch, method, properties, body):
            print(f" [x] Received {body}")

        channel.basic_consume(queue='hello', on_message_callback=callback,
                              auto_ack=True)

        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()