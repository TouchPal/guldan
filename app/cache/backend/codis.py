# -*- coding: utf-8 -*-
import pickle
import time
from redis.client import StrictRedis
from .base import CacheWithLock


class CodisCache(CacheWithLock):
    def __init__(self, redis_url, lock_timeout=None, lock_sleep=None):
        super(CodisCache, self).__init__(lock_timeout=lock_timeout, lock_sleep=lock_sleep)
        self.client = StrictRedis.from_url(redis_url)

    def _value(self, value):
        return {
            "payload": value,
            "metadata": {
                "ct": time.time()
            }
        }

    def get(self, key):
        cached_value = self.client.get(key)
        if cached_value is None:
            return None, -1

        value = pickle.loads(cached_value)
        return value["payload"], value["metadata"]["ct"]

    def set(self, key, value, timeout=None):
        new_value = self._value(value)
        cached_value = pickle.dumps(new_value)
        self.client.set(key, cached_value, ex=timeout)
        return cached_value

    def delete(self, key):
        return self.client.delete(key)


def codis(app, config, args, kwargs):
    return CodisCache(config["CACHE_URL"], lock_timeout=1, lock_sleep=0.1)
