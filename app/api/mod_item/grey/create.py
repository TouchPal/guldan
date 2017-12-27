# -*- coding: utf-8 -*-
from app.api.utils.request_util import item_check
from app.api.mod_item.utils import ensure_item
from app.api.models.item import GreyItem
from app.api.models.sequence import SequenceDual
from app.consts import GREY_ITEM_VERSION_SEQUENCE_NAME


def parse_grey_item_creation_arguments(op_info):
    item_id = item_check(op_info.http_body, "item_id")

    op_info.set_int_attr("item_id", item_id)

    return op_info


def create_grey_item(item_id, item_name, item_data, item_type, item_visibility):
    with SequenceDual.select_for_update(GREY_ITEM_VERSION_SEQUENCE_NAME) as sequence:
        grey_item = GreyItem(item_id, item_name, item_data, item_type, item_visibility, version_id=sequence.value)
        GreyItem.add(grey_item)

    return grey_item


def update_item_for_grey(item):
    item.in_grey = 1


def grey_item_create(op_info):
    op_info = parse_grey_item_creation_arguments(op_info)

    item = ensure_item(op_info.item_id)
    update_item_for_grey(item)
    return create_grey_item(op_info.item_id, item.name, op_info.item_data, op_info.item_type, op_info.visibility)
