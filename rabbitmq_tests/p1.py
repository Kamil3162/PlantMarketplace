import pika
import json
import logging
from threading import Thread

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_url(url: str):
    try:
        # Establish connection
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='localhost',
                port=5672,
                credentials=pika.PlainCredentials(
                    username='myuser',
                    password='mypassword'
                )
            )
        )
        channel = connection.channel()

        # Declare queue
        channel.queue_declare(queue='youtube_queue', durable=True)

        # Create and send message
        message = json.dumps({'url': url})
        channel.basic_publish(
            exchange='',
            routing_key='youtube_queue',
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2  # make message persistent
            )
        )

        logger.info(f"Sent URL: {url}")
        connection.close()

    except Exception as e:
        logger.error(f"Error sending URL {url}: {e}")


def send_urls_in_thread(urls):
    for url in urls:
        send_url(url)


def main():
    urls = [
        "https://www.youtube.com/watch?v=pQI64hD2sJw&t=549s",
        "https://www.youtube.com/watch?v=1zdeYIMANpE",
        "https://www.youtube.com/watch?v=f_6UKzZqb5w",
        "https://www.youtube.com/watch?v=JaSMcfz8gWg",
        "https://www.youtube.com/watch?v=7Dp79jCIedg",
        "https://www.youtube.com/watch?v=NSKxvLWqyOY",
        "https://www.youtube.com/watch?v=f-OdiMHw-is"
    ]

    print("Starting URL sender in background")
    # Start sending in a separate thread
    thread = Thread(target=send_urls_in_thread, args=(urls,))
    thread.daemon = True  # Thread will exit when main program exits
    thread.start()

    print("Main program continues immediately!")
    # Main program can continue doing other things
    # The URLs will be sent in the background


if __name__ == '__main__':
    main()
    # Add this if you want to see all URLs being sent before program exits
    input("Press Enter to exit...")