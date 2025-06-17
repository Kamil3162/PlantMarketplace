from dataclasses import dataclass


class RedisConfig:
    """
        Configuration class for Redis connection parameters.

        Attributes:
            host: Redis server hostname or IP.
            port: Redis server port.
            db: Redis database number.
            password: Optional password for Redis server.
            socket_timeout: Socket timeout in seconds.
            socket_connect_timeout: Socket connection timeout in seconds.
            retry_on_timeout: Whether to retry on timeout.
            max_connections: Maximum number of connections in the pool.
            health_check_interval: How often to check connection health.
            decode_responses: Whether to decode responses from bytes to str.
    """
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    retry_on_timeout: bool = True
    max_connections: int = 10
    health_check_interval: int = 30
    decode_responses: bool = True
