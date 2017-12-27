# -*- coding: utf-8 -*-
from app.api.models.item import GreyItem, Item
from .utils import invalidate_cache_for_grey, ensure_grey_item


def grey_item_delete(item_id):
    grey_item = ensure_grey_item(item_id)
    invalidate_cache_for_grey(item_id, grey_item.item_name, grey_item.item_visibility)
    GreyItem.delete_by_item_id(item_id)
    Item.unset_grey(item_id)
