# -*- coding: utf-8 -*-
from app.cache.core import forced_update
from app.api.mod_puller.pull import pull_item
from app.exc import GulDanException
from app.cache import get_cache_manager


def force_update_puller_cache(item_puller, user_hash_list, item_name):
    try:
        forced_update.force_update()
        for user_hash in user_hash_list:
            try:
                pull_item(item_puller, item_name, user_hash)
            except GulDanException:
                # in case of a changing one item from public to private
                get_cache_manager().delete_memoized(pull_item, item_puller, item_name, user_hash)
    finally:
        forced_update.reset()
