import redis


from .config import RedisConfig

class Connection:
    def __init__(self):
        pass


class RedisClient:
    """
        Client class for Redis operations.

        This class handles the connection to Redis and provides methods
        for various Redis operations. It uses connection pooling for
        better performance and follows the singleton pattern.
    """

    _instance = None
    _logger = logging.getLogger(__name__)

    def __new__(cls, config: Optional[RedisConfig] = None):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config: Optional[RedisConfig] = None):
        """Initialize the Redis client with configuration.

        Args:
            config: Redis configuration parameters.
        """
        if self._initialized:
            return

        self.config = config or RedisConfig()
        self._connection_pool = None
        self._redis = None
        self._initialize_connection()
        self._initialized = True

    def _initialize_connection(self) -> None:
        """Initialize Redis connection pool."""
        try:
            self._connection_pool = redis.ConnectionPool(
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                password=self.config.password,
                socket_timeout=self.config.socket_timeout,
                socket_connect_timeout=self.config.socket_connect_timeout,
                health_check_interval=self.config.health_check_interval,
                max_connections=self.config.max_connections,
                decode_responses=self.config.decode_responses,
                retry_on_timeout=self.config.retry_on_timeout
            )
            self._redis = redis.Redis(connection_pool=self._connection_pool)
            self._logger.info(
                f"Redis connection initialized to {self.config.host}:{self.config.port}/{self.config.db}")
        except redis.RedisError as e:
            self._logger.error(f"Failed to initialize Redis connection: {e}")
            raise

    @property
    def client(self) -> redis.Redis:
        """Get the Redis client instance.

        Returns:
            Redis client instance.
        """
        if self._redis is None:
            self._initialize_connection()
        return self._redis

    def ping(self) -> bool:
        """Check if Redis connection is alive.

        Returns:
            True if connection is alive, False otherwise.
        """
        try:
            return self.client.ping()
        except redis.RedisError as e:
            self._logger.error(f"Redis ping failed: {e}")
            return False

    def get(self, key: str) -> Any:
        """Get a value by key.

        Args:
            key: Redis key.

        Returns:
            Value associated with the key or None if key doesn't exist.
        """
        try:
            return self.client.get(key)
        except redis.RedisError as e:
            self._logger.error(
                f"Redis GET operation failed for key '{key}': {e}")
            return None

    def set(self, key: str, value: Any, ex: Optional[int] = None,
            nx: bool = False, xx: bool = False) -> bool:
        """Set a value with key.

        Args:
            key: Redis key.
            value: Value to store.
            ex: Expiry time in seconds.
            nx: If True, set only if key doesn't exist.
            xx: If True, set only if key exists.

        Returns:
            True if successful, False otherwise.
        """
        try:
            return self.client.set(key, value, ex=ex, nx=nx, xx=xx)
        except redis.RedisError as e:
            self._logger.error(
                f"Redis SET operation failed for key '{key}': {e}")
            return False

    def delete(self, *keys: str) -> int:
        """Delete one or more keys.

        Args:
            keys: One or more Redis keys to delete.

        Returns:
            Number of keys deleted.
        """
        try:
            return self.client.delete(*keys)
        except redis.RedisError as e:
            self._logger.error(f"Redis DELETE operation failed: {e}")
            return 0

    def exists(self, *keys: str) -> int:
        """Check if keys exist.

        Args:
            keys: One or more Redis keys to check.

        Returns:
            Number of keys that exist.
        """
        try:
            return self.client.exists(*keys)
        except redis.RedisError as e:
            self._logger.error(f"Redis EXISTS operation failed: {e}")
            return 0

    def expire(self, key: str, time: int) -> bool:
        """Set key expiration time.

        Args:
            key: Redis key.
            time: Expiration time in seconds.

        Returns:
            True if successful, False otherwise.
        """
        try:
            return self.client.expire(key, time)
        except redis.RedisError as e:
            self._logger.error(
                f"Redis EXPIRE operation failed for key '{key}': {e}")
            return False

    def hset(self, name: str, key: str, value: Any) -> int:
        """Set field in a hash.

        Args:
            name: Hash name.
            key: Hash field.
            value: Value to set.

        Returns:
            1 if field is new, 0 if field existed.
        """
        try:
            return self.client.hset(name, key, value)
        except redis.RedisError as e:
            self._logger.error(
                f"Redis HSET operation failed for hash '{name}': {e}")
            return 0

    def hget(self, name: str, key: str) -> Any:
        """Get field from a hash.

        Args:
            name: Hash name.
            key: Hash field.

        Returns:
            Value associated with field or None if field doesn't exist.
        """
        try:
            return self.client.hget(name, key)
        except redis.RedisError as e:
            self._logger.error(
                f"Redis HGET operation failed for hash '{name}': {e}")
            return None

    def flush_db(self) -> bool:
        """Clear the entire Redis database.

        Returns:
            True if successful, False otherwise.
        """
        try:
            return self.client.flushdb()
        except redis.RedisError as e:
            self._logger.error(f"Redis FLUSHDB operation failed: {e}")
            return False

    def close(self) -> None:
        """Close all connections in the connection pool."""
        if self._connection_pool:
            self._connection_pool.disconnect()
            self._logger.info("Redis connection pool disconnected")