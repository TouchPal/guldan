# -*- coding: utf-8 -*-
from flask import request

from . import item_blueprint
from app.exc import GulDanException
from app.api.mod_puller.pull import pull_item
from app.consts import ITEM_VERSION_SEQUENCE_NAME
from app.api.models.base import Resource
from app.api.models.item import Item
from app.api.models.sequence import SequenceDual
from app.api.utils import request_util, response
from app.api.utils.decorators import audit_modify
from app.api.mod_puller.puller import ItemPuller
from app.cache import get_cache_manager
from .validate import validate_for_item_modify
from .utils import ensure_item, parse_item_options_base, get_normal_fetcher_hash_under_item
from .grey.modify import grey_item_modify_or_create
from app.api.utils.cache import force_update_puller_cache


def parse_item_modify_request(request):
    op_info = parse_item_options_base(request)
    http_body = op_info.http_body

    item_data = request_util.item_check(http_body, "content")
    item_visibility = request_util.item_check(http_body, "private")
    item_type = http_body.get("type", None)

    op_info.item_data = item_data
    op_info.set_visibility(item_visibility)
    op_info.set_item_type(item_type)

    return op_info


def refresh_puller_cache(item_id, item_name, visibility):
    user_hash_list = get_normal_fetcher_hash_under_item(item_id, item_name, visibility)
    item_puller = ItemPuller(item_name)
    force_update_puller_cache(item_puller, user_hash_list, item_name)


def invalidate_cache_for_public(item_name):
    get_cache_manager().delete_memoized(pull_item, ItemPuller(item_name), item_name, None)


@audit_modify(resource_type=Resource.Type.ITEM)
def modify_item_in_db(
    resource_id=None, resource_data=None, item_type=None, visibility=None, in_grey=False, last_updated_at=None
):
    with SequenceDual.select_for_update(ITEM_VERSION_SEQUENCE_NAME) as sequence:
        num_of_affected_rows = Item.update_with_updated_time(
            resource_id, resource_data, item_type, visibility, in_grey,
            updated_at=last_updated_at,
            version_id=sequence.value
        )

    if not num_of_affected_rows:
        raise GulDanException().with_code(409).with_message(
            u"该配置项有修改，请刷新后重试"
        )

    return num_of_affected_rows


def item_modify(
    item_id=None, item_data=None, item_type=None, item_visibility=None, in_grey=False
):
    item = ensure_item(item_id)
    modify_item_in_db(
        resource_id=item_id,
        resource_data=item_data,
        item_type=item_type,
        visibility=item_visibility,
        in_grey=in_grey,
        last_updated_at=item.updated_at
    )
    refresh_puller_cache(item_id, item.name, item_visibility)


@item_blueprint.route("/<int:item_id>", methods=["POST"])
@response.dict_response_deco
def modify_item(item_id):
    op_info = parse_item_modify_request(request)
    validate_for_item_modify(op_info.user_hash, item_id)

    if op_info.grey:
        grey_item_modify_or_create(
            resource_id=item_id,
            resource_data=op_info.item_data,
            item_type=op_info.item_type,
            visibility=op_info.visibility
        )
    else:
        item_modify(
            item_id=item_id,
            item_data=op_info.item_data,
            item_type=op_info.item_type,
            item_visibility=op_info.visibility
        )

    return {
        "msg": "OK"
    }
