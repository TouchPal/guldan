# -*- coding: utf-8 -*-

from werkzeug.contrib.cache import BaseCache
from app.cache.nameregistry import NameRegistry
from app.cache.cluster_adapter import RedisLuaLock


class CacheWithLock(BaseCache):
    def __init__(self, lock_timeout=None, lock_sleep=None):
        super(CacheWithLock, self).__init__()
        self._lock_registry = NameRegistry(self.create_mutex)
        self.lock_timeout = lock_timeout
        self.lock_sleep = lock_sleep
        self.client = None

    def create_mutex(self, key):
        return self.client.lock(u'_lock{0}'.format(key),
                                self.lock_timeout, self.lock_sleep,
                                lock_class=RedisLuaLock)

    def mutex(self, key):
        return self._lock_registry.get(key)