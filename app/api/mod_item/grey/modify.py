# -*- coding: utf-8 -*-
from app.exc import GulDanException
from app.consts import GREY_ITEM_VERSION_SEQUENCE_NAME
from app.api.models.item import GreyItem
from app.api.models.sequence import SequenceDual
from app.api.mod_puller.puller import ItemGreyPuller
from app.api.mod_item.utils import ensure_item
from app.api.utils.cache import force_update_puller_cache
from app.api.utils.db import with_db_flush
from .create import update_item_for_grey, create_grey_item
from .utils import get_grey_fetcher_hash_under_item


def refresh_puller_cache_for_grey(item_id, item_full_name, visibility):
    user_hash_list = get_grey_fetcher_hash_under_item(item_id, item_full_name, visibility)
    grey_puller = ItemGreyPuller(item_full_name)
    force_update_puller_cache(grey_puller, user_hash_list, item_full_name)


@with_db_flush
def modify_grey_item(grey_item, resource_data, item_type, visibility):
    with SequenceDual.select_for_update(GREY_ITEM_VERSION_SEQUENCE_NAME) as sequence:
        num_of_affected_rows = GreyItem.update_with_updated_time(
            grey_item.item_id, resource_data, item_type, visibility,
            version_id=sequence.value,
            updated_at=grey_item.updated_at
        )

    if not num_of_affected_rows:
        raise GulDanException().with_code(409).with_message(
            u"该灰度配置项有修改，请刷新后重试"
        )

    return num_of_affected_rows


def grey_item_modify_or_create(
    resource_id=None, resource_data=None, item_type=0, visibility=None
):
    item = ensure_item(resource_id)
    grey_item = GreyItem.get_by_item_id(resource_id)
    if grey_item:
        modify_grey_item(grey_item, resource_data, item_type, visibility)
        refresh_puller_cache_for_grey(resource_id, item.name, visibility)
    else:
        update_item_for_grey(item)
        create_grey_item(resource_id, item.name, resource_data, item_type, visibility)
