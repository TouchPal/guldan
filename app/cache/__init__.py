# -*- coding: utf-8 -*-
from app import load_app_config
from app import app
from app.cache.core import GuldanCache

cache = None


def get_cache_manager():
    global cache
    if not cache:
        cache = GuldanCache(config={
            'CACHE_TYPE': 'app.cache.backend.codis.codis',
            'CACHE_URL': load_app_config().REDIS_URL
        })
        cache.init_app(app)

    return cache
