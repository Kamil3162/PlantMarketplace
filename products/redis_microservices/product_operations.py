import json
import time
from decimal import Decimal

import redis
import redis.exceptions as exceptions

from django.forms.models import model_to_dict

from data.models import Product
from .config import RedisConfig, Logs
from .utils import (
    get_products_fields,
    redis_operations_handler,
    PerformanceLogger,
    examine_exec_data,
    RedisCache
)


class RedisProductOperations:
    """
    Manages product data caching operations with Redis.

    This class implements robust Redis operations with proper error handling,
    retry logic, and performance optimizations for managing product data.
    """
    _performance_log = PerformanceLogger()

    def __init__(self):
        self.config = RedisConfig()
        self._logger = Logs()
        self.connection = self._establish_connection()
        self._key_prefix = "product"
        self._cache_data = None
        self._cache = RedisCache()

    def _establish_connection(self):
        """Establish a connection to Redis with retry logic and backoff."""
        last_error = None

        for retry in range(self.config.retry_attempts):
            try:
                print(self.config.host)
                print(self.config.port)
                connection = redis.Redis(
                    host=self.config.host,
                    port=self.config.port,
                    socket_timeout=self.config.socket_timeout,
                    decode_responses=True
                    # Auto-decode byte responses for convenience
                )
                connection.ping()
                self._logger.add_info("Succesfull create and connect with redis")
                return connection
            except (exceptions.ConnectionError, exceptions.TimeoutError) as e:
                last_error = e
                # Implement exponential backoff
                backoff_time = 0.1 * (2 ** retry)
                self._logger.add_error("Connection unsucessful: {}".format(e))
                time.sleep(backoff_time)

        # All connection attempts failed
        if isinstance(last_error, exceptions.ConnectionError):
            self._logger.add_error(f"Failed to connect to Redis: all attempts exhausted")
            raise exceptions.ConnectionError(
                f"Failed to establish connection: {last_error}")
        elif isinstance(last_error, exceptions.TimeoutError):
            self._logger.add_error(f"Redis connection timeout: all attempts exhausted")
            raise exceptions.TimeoutError(
                f"Connection timed out: {last_error}")
        else:
            self._logger.add_error(f"Unknown Redis connection error: {last_error}")
            raise exceptions.RedisError(f"Connection failed: {last_error}")

    def format_key(self, product_key):
        """
        Format product key with proper prefix

        Args:
            product_key (str): product UUID or ID

        Returns:
            Formatted redis key with prefix
        """
        return f"{self._key_prefix}:{product_key}"

    def validate_product_data(self, product_data: dict):
        """
        Validate product data

        Args:
            product_data (dict): product data with all fields from DB

        Returns:
            Dictionary with validated product data

        Raises:
            authenticate.DataError: If required fields are missing
        """
        if not product_data:
            raise exceptions.DataError("Product data cannot be empty")

        product_fields = get_products_fields()
        print(product_fields)
        validated_data = {}

        # Extract valid fields and convert data types if needed
        for key, value in product_data.items():
            if key in product_fields:
                # Convert numeric values to strings for Redis compatibility
                if isinstance(value, (int, float)):
                    validated_data[key] = str(value)
                else:
                    validated_data[key] = value

        # Check required fields
        required_fields = ['name', 'price']
        missing_fields = [field for field in required_fields if
                          field not in validated_data]
        if missing_fields:
            raise exceptions.DataError(
                f"Missing required fields: {', '.join(missing_fields)}")

        return validated_data

    @redis_operations_handler
    def add_product(self, **kwargs):
        """
        Add product to cache

        Args:
            **kwargs (dict): product data with UUID and Product fields

        Returns:
            True on success, False on failure
        """
        if 'key' not in kwargs:
            raise exceptions.DataError("Product key is required")

        key = self.format_key(kwargs.pop('key'))
        product_data = self.validate_product_data(kwargs)

        # Add timestamps
        product_data['created_at'] = str(int(time.time()))

        result = self.connection.hset(key, mapping=product_data)

        # Set expiration if TTL is configured
        if hasattr(self.config, 'ttl') and self.config.ttl > 0:
            self.connection.expire(key, self.config.ttl)

        self._logger.add_info(f"Added product: {key} with {len(product_data)} fields")
        return product_data

    @redis_operations_handler
    def exists(self, product_key):
        """
        Check if a product exists in Redis

        Args:
            product_key: The product ID or key

        Returns:
            bool: True if product exists, False otherwise
        """
        key = self.format_key(product_key)
        exists = self.connection.exists(key)
        return bool(exists)

    @redis_operations_handler
    def modify_product(self, **kwargs):
        """
        Modify an existing product in Redis

        Args:
            **kwargs: Product data, must include 'key'

        Returns:
            bool: True if product was successfully modified
        """
        if 'key' not in kwargs:
            raise exceptions.DataError("Product key is required")

        product_key = kwargs.pop('key')
        key = self.format_key(product_key)

        # Check if product exists
        if not self.exists(product_key):
            raise exceptions.ResponseError(
                f"Product {product_key} does not exist")

        # Get existing data to merge with updates
        existing_data = self.connection.hgetall(key)
        if not existing_data:
            raise exceptions.ResponseError(
                f"Product {product_key} exists but data is missing")

        # Update with new values
        updated_data = {**existing_data, **kwargs}

        # Validate the merged data
        product_data = self.validate_product_data(updated_data)

        # Add update timestamp
        product_data['updated_at'] = str(int(time.time()))

        # Update data in Redis
        result = self.connection.hset(key, mapping=product_data)

        # Reset TTL if configured
        if hasattr(self.config, 'ttl') and self.config.ttl > 0:
            self.connection.expire(key, self.config.ttl)

        # Invalidate cache if it exists
        self.delete_from_cache(product_key)

        logger.info(f"Modified product: {key} with {len(product_data)} fields")
        return True

    @redis_operations_handler
    def delete_product(self, product_key):
        """
        Delete a product from Redis

        Args:
            product_key: The product ID or key

        Returns:
            bool: True if product was deleted, False otherwise
        """
        key = self.format_key(product_key)

        # Check if product exists
        exists = self.connection.exists(key)

        if not exists:
            logger.warning(
                f"Attempted to delete non-existent product: {product_key}")
            return False

        # Delete product
        result = self.connection.delete(key)

        # Also invalidate any cached version
        self.delete_from_cache(product_key)

        logger.info(f"Deleted product: {product_key}")
        return bool(result)

    @redis_operations_handler
    def get_product(self, product_key):
        """
        Get product data from Redis and handle caching strategy

        Args:
            product_key (str): product UUID or ID

        Returns:
            dict: Product data or None if not found
        """
        key = self.format_key(product_key)
        try:
            redis_data = self.connection.hgetall(key)
            if not redis_data:
                self._logger.add_info(
                    f"Product {product_key} not found in Redis, trying database")

                product = Product.objects.get(id=product_key)
                product_dict = model_to_dict(product)

                cleaned_data = self._prepare_product_for_redis(product_dict)

                success = self.add_product(key=product_key, **cleaned_data)
                self._logger.add_info(f"Redis added product: {product_key}")
                return success

            self._logger.add_info(f"Redis hit for product: {product_key}")
            return redis_data

        except Product.DoesNotExist:
            self._logger.add_error(f"Product {product_key} not found in database")
            return None
        except redis.exceptions.DataError as e:
            self._logger.add_error(e)
            raise redis.exceptions.DataError(f"Product does not exist")


    @redis_operations_handler
    def delete_from_cache(self, product_key):
        """
        Delete a product from the memory cache

        Args:
            product_key: The product ID or key

        Returns:
            bool: True if successfully processed
        """
        try:
            key = self.format_key(product_key)

            if self._cache_data is None:
                self._cache_data = self.connection.get_cache()

            self._cache_data.delete_by_redis_keys(key)
            logger.debug(f"Deleted {product_key} from cache")
            return True
        except KeyError:
            # Not in cache - not an error
            logger.debug(f"Key {product_key} not found in cache")
            return True

    @redis_operations_handler
    def clear_cache(self):
        """
        Clear the entire memory cache

        Returns:
            bool: True if cache was successfully cleared
        """
        if self._cache_data is None:
            self._cache_data = self.connection.get_cache()

        self._cache_data.flush()
        logger.info("Cache cleared")
        return True

    @redis_operations_handler
    def fetch_latest_cache(self):
        """
        Clear and fetch the latest cache data

        Returns:
            The latest cache object
        """
        self.clear_cache()
        self._cache_data = self.connection.get_cache()
        logger.info("Fetched latest cache data")
        return self._cache_data

    @redis_operations_handler
    def get_many_products(self, product_keys):
        """
        Efficiently retrieve multiple products at once using pipelining

        Args:
            product_keys (list): List of product IDs or keys

        Returns:
            dict: Dictionary of {key: product_data} for all found products
        """
        if not product_keys:
            return {}

        # Format all keys
        keys = [self.format_key(key) for key in product_keys]

        # Use pipeline for better performance
        pipe = self.connection.pipeline()
        for key in keys:
            pipe.hgetall(key)

        # Execute all commands in a single request
        results = pipe.execute()

        # Organize results
        products = {}
        for i, key in enumerate(product_keys):
            if results[i]:  # Only include products that were found
                products[key] = results[i]

        # Handle missing products if needed
        missing_keys = [key for i, key in enumerate(product_keys) if
                        not results[i]]
        if missing_keys:
            logger.info(f"Products not found in Redis: {missing_keys}")
            # Could implement database fallback here

        return products

    @redis_operations_handler
    def insert_db_products(self):
        """
    Load all products from PostgreSQL database into Redis.

    This method is typically called during application startup or when
    refreshing the cache. It iterates through all products in the database,
    converts them to a Redis-friendly format, and stores each as a separate
    Redis hash.

    Returns:
        dict: Dictionary of all products with product IDs as keys

    Raises:
        RedisError: If connection to Redis fails
        DatabaseError: If database retrieval fails
    """
        self._logger.add_info("Starting to load products from database into Redis")

        try:
            # Verify Redis connection is active
            if not self.connection.ping():
                raise redis.exceptions.ConnectionError("Redis connection test failed")

            # Get all products from database
            products = Product.objects.all()
            self._logger.add_info(f"Retrieved {products.count()} products from database")

            # Prepare result container
            products_data = {}

            # Use pipeline for better performance with multiple operations
            pipeline = self.connection.pipeline()

            # Process each product
            for product in products:
                product_id = str(product.id)
                redis_key = f"product:{product_id}"

                # Convert model to dictionary
                product_dict = model_to_dict(product)

                # Convert non-serializable types to Redis-compatible formats
                serializable_dict = self._prepare_product_for_redis(product_dict)

                # Add to our return data
                products_data[product_id] = serializable_dict

                # Queue Redis hash creation in pipeline
                pipeline.hset(
                    name=redis_key,  # The Redis key for this product
                    mapping=serializable_dict  # Fields and values for this product
                )

                # Set TTL if configured
                if hasattr(self.config, 'ttl') and self.config.ttl > 0:
                    pipeline.expire(redis_key, self.config.ttl)

            # Execute all Redis commands in a single network operation
            pipeline.execute()

            # pipeline.hgetall(name='product:621e73fe-07cd-432e-812d-09460944934d')

            result = pipeline.execute()

            self._logger.add_info(f"Successfully stored {len(products_data)} products in Redis")
            return products_data

        except redis.exceptions.RedisError as e:
            error_msg = f"Redis error while storing products: {str(e)}"
            self._logger.add_error(error_msg)
            raise redis.exceptions.RedisError(error_msg)

        except Exception as e:
            error_msg = f"Unexpected error storing products: {str(e)}"
            self._logger.add_error(error_msg)
            raise

    @redis_operations_handler
    @examine_exec_data(retry=5, performanceLogger=_performance_log)
    def fetch_all(self):
        result = self.connection.scan(cursor=0, match='product*', count=1000)
        return result

    def _prepare_product_for_redis(self, product_dict):
        """
        Convert a product dictionary to Redis-compatible format.

        Args:
            product_dict (dict): Original product dictionary from model_to_dict

        Returns:
            dict: Product dictionary with all values in Redis-compatible format
        """
        serializable_dict = {}

        for key, value in product_dict.items():
            if value is None:
                serializable_dict[key] = ""
            elif isinstance(value, Decimal):
                serializable_dict[key] = str(float(value))  # Store as string to preserve precision
            elif isinstance(value, (dict, list)):
                serializable_dict[key] = json.dumps(value)
            elif isinstance(value, (int, float, str, bool)):
                serializable_dict[key] = value
            else:
                serializable_dict[key] = str(value)

        return serializable_dict

