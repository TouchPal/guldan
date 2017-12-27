# -*- coding: utf-8 -*-
from flask import request

from . import item_blueprint
from app.api.utils.privileges import get_privileges_for_resource
from app.exc import GulDanException
from validate import validate_for_item_view
from app.api.models.base import Resource
from app.api.utils import response
from app.api.utils.resource import get_one_modifier
from app.api.mod_item.validate import can_user_modify_item
from .utils import ensure_item, parse_item_options_base
from .grey.display import get_item_grey


def can_not_view_response(item_id):
    modifier = get_one_modifier(Resource.Type.ITEM, item_id)

    raise GulDanException().with_code(403).with_message(u"你没有权限查看该项目, 可以向{}申请权限".format(
        modifier["user_name"]
    ))


@item_blueprint.route("/<int:item_id>", methods=["GET"])
@response.dict_response_deco
def get_item(item_id):
    op_info = parse_item_options_base(request)
    item = ensure_item(item_id)
    try:
        validate_for_item_view(
            op_info.user_hash,
            item_id
        )
    except GulDanException:
        return can_not_view_response(item_id)

    if op_info.grey:
        item_info = get_item_grey(item_id)
        item_info["parent_id"] = item.parent_id
    else:
        item_info = item.to_dict()

    if can_user_modify_item(item.id, op_info.user_hash):
        privileges_list = get_privileges_for_resource(item.id, Resource.Type.ITEM)
        item_info["privileges"] = privileges_list
        item_info["access_mode"] = "modifier"
    else:
        item_info["access_mode"] = "viewer"

    return {
        "msg": "OK",
        "data": item_info
    }

