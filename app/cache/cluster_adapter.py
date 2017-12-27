# -*- coding: utf-8 -*-
import logging
from redis.lock import LuaLock

logger = logging.getLogger(__name__)


class RedisLuaLock(LuaLock):
    @classmethod
    def lua_acquire(cls, keys, args, client):
        args = tuple(keys) + tuple(args)
        return client.eval(cls.LUA_ACQUIRE_SCRIPT, len(keys), *args)

    @classmethod
    def lua_release(cls, keys, args, client):
        args = tuple(keys) + tuple(args)
        try:
            client.eval(cls.LUA_RELEASE_SCRIPT, len(keys), *args)
        except Exception:
            logger.warn("Fail to release redis lua lock")
        return True

    @classmethod
    def lua_extend(cls, keys, args, client):
        args = tuple(keys) + tuple(args)
        return client.eval(cls.LUA_EXTEND_SCRIPT, len(keys), *args)

