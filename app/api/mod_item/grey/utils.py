# -*- coding: utf-8 -*-

from app.api.models.item import GreyItem, Item
from app.exc import GulDanException
from app.api.mod_puller.puller import ItemGreyPuller
from app.api.mod_puller.pull import pull_item
from app.cache import cache
from app.kv import get_kv_manager
from app.api.mod_item.utils import get_user_hash_from_db


def ensure_grey_item(item_id):
    grey_item = GreyItem.get_by_item_id(item_id)
    if not grey_item:
        item = Item.get_by_id(item_id)
        if not item:
            raise GulDanException().with_code(404).with_message(
                u"找不到配置项(id:{})".format(item_id)
            )
        grey_item = GreyItem(item.id, item.name, item.data, item.type, item.visibility)

    return grey_item


def ensure_grey_item_by_name(item_name):
    grey_item = GreyItem.get_by_item_name(item_name)
    if not grey_item:
        item = Item.get_by_name(item_name)
        if not item:
            raise GulDanException().with_code(404).with_message(
                u"找不到配置项(name:{})".format(item_name)
            )
        grey_item = GreyItem(item.id, item.name, item.data, item.type, item.visibility)

    return grey_item


def get_grey_fetcher_hash_from_kv(item_name):
    user_hashes = set()
    for normal_fetcher in get_kv_manager().get_item_grey_fetchers(item_name):
        user_hashes.add(normal_fetcher.get("puller_hash", None))

    return user_hashes


def get_grey_fetcher_hash_under_item(item_id, item_name, visibility):
    user_hashes_from_kv = get_grey_fetcher_hash_from_kv(item_name)
    user_hashes_from_db = get_user_hash_from_db(item_id, visibility)

    return user_hashes_from_kv | user_hashes_from_db


def invalidate_cache_for_grey(item_id, item_name, visibility):
    user_hash_list = get_grey_fetcher_hash_under_item(item_id, item_name, visibility)
    grey_puller = ItemGreyPuller(item_name)
    for user_hash in user_hash_list:
        cache.delete_memoized(pull_item, grey_puller, item_name, user_hash)