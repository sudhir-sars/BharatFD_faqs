import redis
import json
from django.db import transaction


class RedisHandler:
    def __init__(self):
        self.client = redis.StrictRedis(
            host="localhost", port=6379, db=1, decode_responses=True
        )

    def get_cache(self, key):
        value = self.client.get(key)
        if value:
            try:
                return json.loads(value)  # Deserialize the cached data
            except json.JSONDecodeError:
                return value  # Return raw value if deserialization fails
        return None

    def set_cache(self, key, value, timeout=3600):
        # Ensure that the value passed to Redis is serializable
        if isinstance(
            value, (dict, list)
        ):  # If value is a dictionary or list, serialize it
            value = json.dumps(value)
        elif not isinstance(value, str):  # If it's not a string, convert it to a string
            value = str(value)

        # Now that it's serializable, store it in Redis
        self.client.setex(key, timeout, value)

    @transaction.atomic
    def set_cache_with_transaction(self, key, value, timeout=3600):
        self.set_cache(key, value, timeout)
