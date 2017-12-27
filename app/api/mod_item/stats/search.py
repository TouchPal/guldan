# -*- coding: utf-8 -*-
from flask import request

from app.api.mod_item import item_blueprint
from app.api.mod_item.display import can_not_view_response
from app.api.mod_item.validate import validate_for_item_view
from app.api.utils import response
from app.exc import GulDanException
from app.api.utils import request_util


def parse_item_stats_search_request(request):
    op_info = request_util.parse_request(request)

    op_info.ip = request.args.get("ip", None)
    op_info.grey = request.args.get("grey", None)
    op_info.cid = request.args.get("cid", None)
    op_info.cversion = request.args.get("cversioin", None)

    return op_info


@item_blueprint.route("/<int:item_id>/stats/search", methods=["GET"])
@response.dict_response_deco
def item_puller_stats(item_id):
    op_info = parse_item_stats_search_request(request)

    try:
        validate_for_item_view(
            op_info.user_hash,
            item_id
        )
    except GulDanException:
        return can_not_view_response(item_id)

    return {
        "msg": "OK"
    }
