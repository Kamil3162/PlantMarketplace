

def client():
    from .product_operations import RedisProductOperations
    return RedisProductOperations()

__all__ = ['client']