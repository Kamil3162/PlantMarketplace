import celery

from config import ConfigCelery

class CeleryOperations:
    def __init__(self, config:ConfigCelery):
        self.app = celery.Celery(
            config.name,
            broker=config.broker,
            backend=config.result_backend
        )

        self.app.conf.update(
            task_serializer=config.task_serializer,
            accept_content=config.accept_content,
            result_serializer=config.result_serializer,
            timezone=config.timezone,
            enable_utc=config.enable_utc
        )

    def register_tack(self, task):
        self.app.register_task(task)

    def send_email(self):
        pass




