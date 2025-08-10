from django.core.cache import cache
from django.conf import settings
import redis
import json
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)

class RedisClient:
    """
    Enhanced Redis client with connection pooling and error handling
    """
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls)
            # Initialize connection pool
            cls._pool = redis.ConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                max_connections=10,  # Adjust based on your needs
                socket_timeout=5,    # 5 seconds timeout
                retry_on_timeout=True
            )
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'redis_client'):
            self.redis_client = redis.Redis(
                connection_pool=self._pool,
                retry_on_timeout=True
            )

    def set_json(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """Store JSON serializable data in Redis with error handling"""
        try:
            serialized_value = json.dumps(value)
            return self.redis_client.set(key, serialized_value, ex=timeout)
        except redis.RedisError as e:
            logger.error(f"Redis error setting key {key}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error setting Redis key {key}: {e}")
            return False

    def get_json(self, key: str, default: Any = None) -> Any:
        """Retrieve and deserialize JSON data from Redis with error handling"""
        try:
            value = self.redis_client.get(key)
            return json.loads(value) if value else default
        except redis.RedisError as e:
            logger.error(f"Redis error getting key {key}: {e}")
            return default
        except Exception as e:
            logger.error(f"Error getting Redis key {key}: {e}")
            return default

    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a numeric value in Redis with error handling"""
        try:
            return self.redis_client.incr(key, amount)
        except redis.RedisError as e:
            logger.error(f"Redis error incrementing key {key}: {e}")
            return None

    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching the pattern with error handling"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except redis.RedisError as e:
            logger.error(f"Redis error deleting pattern {pattern}: {e}")
            return 0

    def set_lock(self, lock_name: str, timeout: int = 60) -> bool:
        """Implement a distributed lock with error handling"""
        try:
            return bool(self.redis_client.set(
                f"lock:{lock_name}",
                "1",
                ex=timeout,
                nx=True
            ))
        except redis.RedisError as e:
            logger.error(f"Redis error setting lock {lock_name}: {e}")
            return False

    def release_lock(self, lock_name: str) -> bool:
        """Release a distributed lock with error handling"""
        try:
            return bool(self.redis_client.delete(f"lock:{lock_name}"))
        except redis.RedisError as e:
            logger.error(f"Redis error releasing lock {lock_name}: {e}")
            return False

# Create a singleton instance
redis_client = RedisClient()