# -*- coding: utf-8 -*-
import time
import functools
import logging
from flask_caching import Cache
from .lock import Lock

logger = logging.getLogger(__name__)


class GuldanCache(Cache):
    def __init__(self, **kwargs):
        super(GuldanCache, self).__init__(**kwargs)

    def _make_cache_key(self, f, *args, **kwargs):
        namespace = "{}:{}:v2".format(f.__module__, f.__name__)

        def unicode_to_str(u):
            if isinstance(u, unicode):
                return u.encode("utf-8")
            return str(u)

        def pair_to_str(pair):
            k, v = pair
            return k, unicode_to_str(v)

        args = tuple(map(unicode_to_str, args))
        tuples = sorted(map(pair_to_str, kwargs.iteritems()))

        return "{}|{}{}".format(namespace, args, tuples)

    def memoize(self, timeout=None, make_name=None, unless=None,
                forced_update=None):
        def memoize(f):
            def get_or_create(key, creator, expiration_time=None):
                def get_value():
                    value, createdtime = self.cache.get(key)
                    if createdtime < 0:
                        return None

                    return value, createdtime

                def generate_value():
                    created_value = creator()
                    cached_value = self.cache.set(key, created_value, expiration_time)
                    return created_value, time.time()

                with Lock(
                    self.cache.mutex(key),
                    generate_value,
                    get_value,
                    expiration_time
                ) as value:
                    return value

            def try_to_get_from_cache(*args, **kwargs):
                #: bypass cache
                if self._bypass_cache(unless, f, *args, **kwargs):
                    return f(*args, **kwargs)

                cache_key = decorated_function.make_cache_key(
                    f, *args, **kwargs
                )

                @functools.wraps(f)
                def call_func():
                    return f(*args, **kwargs)

                if callable(forced_update) and forced_update() is True:
                    rv = None
                else:
                    rv = get_or_create(cache_key, call_func, expiration_time=timeout)

                if rv is None:
                    rv = f(*args, **kwargs)

                    self.cache.set(
                        cache_key, rv,
                        timeout=decorated_function.cache_timeout
                    )

                return rv

            @functools.wraps(f)
            def decorated_function(*args, **kwargs):
                try:
                    return try_to_get_from_cache(*args, **kwargs)
                except:
                    logger.exception("error trying to get from cache")
                    return f(*args, **kwargs)

            decorated_function.uncached = f
            decorated_function.cache_timeout = timeout
            decorated_function.make_cache_key = self._make_cache_key
            decorated_function.delete_memoized = \
                lambda: self.delete_memoized(f)

            return decorated_function
        return memoize


class ForcedUpdate(object):
    def __init__(self):
        self._forced_update = False

    def __call__(self, *args, **kwargs):
        return self._forced_update

    def force_update(self):
        self._forced_update = True

    def reset(self):
        self._forced_update = False


forced_update = ForcedUpdate()
