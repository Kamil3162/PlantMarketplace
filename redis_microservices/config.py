from dataclasses import dataclass
import logging
import redis

@dataclass
class RedisConfig:
    host:str = os.getenv("REDIS_HOST", "localhost")
    port:int = os.getenv("REDIS_PORT", 6379)
    db:int = 0
    timeout:int = 5
    socket_timeout: float = 3.0
    socket_connect_timeout: float = 3.0
    retry_attempts: int = 3
    retry_delay: float = 0.1
    ttl: int = 3600  # Default TTL of 1 hour

class Logs:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.info_handler = logging.FileHandler(filename="info.log", mode="w")
        self.error_handler = logging.FileHandler(filename="errors.log", mode="w")

    def _setup_handlers(self):
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        self.info_handler.setLevel(logging.INFO)
        self.info_handler.setFormatter(formatter)

        self.error_handler.setLevel(logging.ERROR)
        self.error_handler.setFormatter(formatter)

        self.logger.addHandler(self.info_handler)
        self.logger.addHandler(self.error_handler)

    def add_info(self, message):
        self.logger.info(message)

    def add_error(self, message):
        self.logger.error(message)


def retry_on_connection_error(max_retries=3, backoff_factor=0.3):
    """Decorator for retrying operations that may fail due to connection issues.

    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Exponential backoff multiplier

    Returns:
        Decorated function with retry logic
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (redis_exceptions.ConnectionError,
                        redis_exceptions.TimeoutError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        sleep_time = backoff_factor * (2 ** attempt)
                        logger.warning(
                            f"Redis operation failed (attempt {attempt + 1}/{max_retries}): {e}. "
                            f"Retrying in {sleep_time:.2f}s")
                        time.sleep(sleep_time)
                    else:
                        logger.error(
                            f"Redis operation failed after {max_retries} attempts: {e}")

            # If we get here, all retries failed
            raise last_exception

        return wrapper

    return decorator