# -*- coding: utf-8 -*-
from flask import request

from app.api.mod_item import item_blueprint
from app.api.mod_item.display import can_not_view_response
from app.api.mod_item.validate import validate_for_item_view
from app.api.models.item import Item
from app.api.utils import response, request_util
from app.exc import GulDanException
from app.kv import get_kv_manager


def get_puller_stats_for_name(item_name):
    normal_fetchers = get_kv_manager().get_item_normal_fetchers(item_name)
    grey_fetchers = get_kv_manager().get_item_grey_fetchers(item_name)

    return grey_fetchers + normal_fetchers


def get_item_puller_stats(item_id):
    item_name = Item.get_name_by_id(item_id)
    return item_name, get_puller_stats_for_name(item_name)


def parse_puller_stats_arguments(request):
    return request_util.parse_request(request)


@item_blueprint.route("/<int:item_id>/stats", methods=["GET"])
@response.dict_response_deco
def item_puller_stats(item_id):
    op_info = parse_puller_stats_arguments(request)

    try:
        validate_for_item_view(
            op_info.user_hash,
            item_id
        )
    except GulDanException:
        return can_not_view_response(item_id)

    item_name, stats_list = get_item_puller_stats(item_id)
    return {
        "msg": "OK",
        "data": {
            "name": item_name,
            "stats": stats_list
        }
    }
