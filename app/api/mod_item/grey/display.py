# -*- coding: utf-8 -*-
from app.api.mod_item.grey.utils import ensure_grey_item
from app.kv import get_kv_manager


def get_grey_item_fetchers(item_name):
    return get_kv_manager().get_item_grey_fetchers(item_name)


def get_item_grey(item_id):
    grey_item = ensure_grey_item(item_id)
    grey_item_fetchers = get_grey_item_fetchers(grey_item.item_name)

    grey_item_info = grey_item.to_dict()
    grey_item_info["fetchers"] = list(grey_item_fetchers)

    return grey_item_info
