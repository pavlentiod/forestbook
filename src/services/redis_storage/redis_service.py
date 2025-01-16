import pickle
from typing import Optional, Any

import redis

from src.config import settings


class RedisStorage:
    """
    Class for managing Redis storage with serialization and deserialization using pickle.
    """

    def __init__(self):
        self.redis_client = redis.Redis(connection_pool=settings.redis.redis_connection_pool)

    def get(self, key: str) -> Optional[Any]:
        """
        Get data from Redis and deserialize it using pickle.
        """
        print(f"Get data from cache: {key}")
        data = self.redis_client.get(key)
        if data is not None:
            return pickle.loads(data)
        return None

    def set(self, key: str, value: Any, ex: Optional[int] = 3600):
        """
        Serialize data using pickle and store it in Redis with an optional expiration time.
        """
        serialized_data = pickle.dumps(value)
        self.redis_client.set(key, serialized_data, ex=ex)

    def delete(self, key: str):
        """
        Delete a key from Redis.
        """
        self.redis_client.delete(key)
