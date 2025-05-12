from .celery_worker import ops_celery

result = ops_celery.send_products_email()

print(f"Zadanie zostało dodane do kolejki. ID zadania: {result['task_id']}")