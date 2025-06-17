import aio_pika
import asyncio
import json
import logging
import os
from pytubefix import YouTube
from typing import Set, Dict
from asyncio import Task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ParallelYouTubeConsumer:
    def __init__(self, max_parallel_downloads: int = 3):
        self.connection = None
        self.channel = None
        self.output_dir = "venv/PlantMarketplace/mp3"
        self.max_parallel_downloads = max_parallel_downloads
        self.active_tasks: Set[Task] = set()
        self.processing_urls: Dict[str, Task] = {}
        os.makedirs(self.output_dir, exist_ok=True)

    async def connect(self):
        max_retries = 5
        retry_delay = 5  # sec
        for attempt in range(max_retries):
            try:
                self.connection = await aio_pika.connect_robust(
                    "amqp://myuser:mypassword@localhost:5672/"
                )
                logger.info("Connection Successful")

                self.channel = await self.connection.channel()
                # Zwiększamy prefetch_count, aby otrzymywać więcej wiadomości jednocześnie
                await self.channel.set_qos(
                    prefetch_count=self.max_parallel_downloads)
                logger.info("Channel created and QoS set")
                return

            except Exception as e:
                logger.error(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error(
                        "Max retries reached. Could not establish connection.")
                    raise

    async def download_and_save(self, url: str) -> str:
        """Download and save to MP3"""
        try:
            # Run download in thread pool to not block event loop
            loop = asyncio.get_event_loop()
            yt = await loop.run_in_executor(None, YouTube, url)

            # Get audio stream
            audio = yt.streams.filter(only_audio=True).first()
            if not audio:
                raise Exception("No audio stream found")

            # Download and save as MP3
            output_file = await loop.run_in_executor(
                None,
                lambda: audio.download(self.output_dir)
            )
            mp3_file = output_file.rsplit(".", 1)[0] + ".mp3"
            os.rename(output_file, mp3_file)

            return mp3_file

        except Exception as e:
            logger.error(f"Download error for {url}: {str(e)}")
            raise

    async def process_message(self, message: aio_pika.IncomingMessage):
        """Process single message"""
        try:
            # Parse message
            data = json.loads(message.body.decode())
            url = data.get('url')
            if not url:
                raise ValueError("No URL in message")

            logger.info(f"Starting processing: {url}")

            # Download and save
            output_file = await self.download_and_save(url)
            logger.info(f"Saved as: {output_file}")

            # Acknowledge message only after successful processing
            await message.ack()

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            # Reject and requeue message on error
            await message.reject(requeue=True)
        finally:
            # Remove task from active tasks
            if url in self.processing_urls:
                del self.processing_urls[url]

    def cleanup_done_tasks(self):
        """Remove completed tasks from the active set"""
        done_tasks = {task for task in self.active_tasks if task.done()}
        self.active_tasks.difference_update(done_tasks)
        for task in done_tasks:
            # Ensure any core are logged
            if task.exception():
                logger.error(f"Task failed with error: {task.exception()}")

    async def run(self):
        try:
            # Connect
            await self.connect()

            # Setup queue
            queue = await self.channel.declare_queue(
                "youtube_queue",
                durable=True
            )

            logger.info(
                f"Waiting for YouTube URLs... (max {self.max_parallel_downloads} parallel downloads)")

            # Start consuming
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    # Clean up completed tasks
                    self.cleanup_done_tasks()

                    # Wait if we've reached max parallel downloads
                    while len(
                            self.active_tasks) >= self.max_parallel_downloads:
                        await asyncio.sleep(1)
                        self.cleanup_done_tasks()

                    # Create and start new task
                    task = asyncio.create_task(self.process_message(message))
                    self.active_tasks.add(task)

                    # Store URL-task mapping
                    try:
                        data = json.loads(message.body.decode())
                        url = data.get('url')
                        if url:
                            self.processing_urls[url] = task
                    except Exception as e:
                        logger.error(f"Error parsing message: {e}")

        except Exception as e:
            logger.error(f"Consumer error: {e}")
        finally:
            # Wait for all active tasks to complete before shutting down
            if self.active_tasks:
                await asyncio.gather(*self.active_tasks,
                                     return_exceptions=True)
            if self.connection:
                await self.connection.close()


async def main():
    # Utworzenie konsumera z maksymalnie 3 równoległymi pobraniami
    consumer = ParallelYouTubeConsumer(max_parallel_downloads=3)
    await consumer.run()


if __name__ == '__main__':
    asyncio.run(main())