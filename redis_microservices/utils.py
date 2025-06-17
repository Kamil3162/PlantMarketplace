import functools
import json
import decimal
import logging
import os.path
import time

import cachetools
from redis import exceptions

from products.models import Product

from django.core.files import File
from django.db.models import FileField
from django.db.models.fields import CharField

def get_products_fields():
    try:
        return [field.name for field in Product._meta.fields]
    except AttributeError as e:
        raise AttributeError(f'Product Meta: {e}')

def redis_operations_handler(function):
    """Decorator for handling Redis operation core consistently."""
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        try:
            result = function(*args, **kwargs)
            return result
        except exceptions.DataError as e:
            raise exceptions.DataError(f"Invalid data format: {e}")
        except exceptions.TimeoutError as e:
            raise exceptions.TimeoutError(f"Operation timed out: {e}")
        except exceptions.ConnectionError as e:
            raise exceptions.ConnectionError(f"Connection failed: {e}")
        except exceptions.RedisError as e:
            raise exceptions.RedisError(f"Redis operation failed: {e}")
        except Exception as e:
            raise exceptions.RedisError(f"Unexpected error: {e}")
    return wrapper

class CustomProductEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return int(o)
        elif isinstance(o, (File, FileField)):
            return str(o) if o else None
        return super().default(o)


def examine_exec_data(retry=5, performanceLogger=None):
    def check(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            if retry:
                for _ in range(retry):
                    try:
                        start_time = time.perf_counter()
                        result = function(*args, **kwargs)
                        end_time = time.perf_counter()
                        performanceLogger.add_log(f"Exec takes time:{end_time-start_time}")
                    except Exception as e:
                        performanceLogger.add_log(f"Error: {str(e)}")
                return result
            else:
                try:
                    start_time = time.perf_counter()
                    result = function(*args, **kwargs)
                    end_time = time.perf_counter()
                    performanceLogger.add_log(f"Exec takes time:{end_time-start_time}")
                except Exception as e:
                    performanceLogger.add_log(f"Error: {str(e)}")
        return wrapper
    return check


class PerformanceLogger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.logger.setLevel(level=logging.INFO)
        self.file_handler = logging.FileHandler(
            os.path.join(self.path, "performence.logs"), mode="a"
        )

        self._setup_handlers()

    def _setup_handlers(self):
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.file_handler.setLevel(level=logging.INFO)
        self.file_handler.setFormatter(formatter)

        self.logger.addHandler(self.file_handler)

    def add_log(self, message):
        self.logger.info(message)


class RedisCache:
    def __init__(self):
        self._cache = cachetools.TTLCache(maxsize=10000, ttl=300)

    def add_data(self, key, data):
        if key in self._cache.keys():
            return False
        else:
            self._cache[key] = data
            return True

    def get_data(self, key):
        try:
            result = self._cache['test']
            return result
        except KeyError as error:
            raise KeyError("Following key does not exist")

    def delete_data(self, key):
        if key in self._cache.keys():
            self._cache.pop(key)
            return True
        return False

    def modify_data(self, key, data):
        try:
            data = self._cache[key]
            self._cache[key] = data
        except KeyError:
            raise "Following key does not exist"

