
def redis_product_client():
    from .product_operations import RedisProductOperations
    return RedisProductOperations()

__all__ = ['redis_product_client']