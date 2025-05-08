import functools
from redis import exceptions
from products.models import Product

def get_products_fields():
    try:
        return Product._meta.fields
    except AttributeError as e:
        raise AttributeError(f'Product Meta: {e}')


def redis_operations_handler(function):
    """Decorator for handling Redis operation exceptions consistently."""
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

