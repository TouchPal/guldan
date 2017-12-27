# -*- coding: utf-8 -*-

from flask import request
from . import item_versions_blueprint
from app.api.utils.response import dict_response_deco
from app.api.utils import request_util
from app.api.mod_item.validate import validate_for_item_modify
from app.api.models.version import ResourceVersion
from app.api.models.base import Resource
from app.api.models.item import Item


def parse_request_args(request):
    op_info = request_util.parse_request(request)

    offset = request_util.url_param_check(op_info, "offset")
    limit = request_util.url_param_check(op_info, "limit")
    order = request_util.url_param_check(op_info, "order")

    op_info.set_offset(offset)
    op_info.set_limit(limit)

    if order == "desc":
        op_info.desc = True
    else:
        op_info.desc = False

    return op_info


def get_item_versions(item_id, limit=100, offset=0, desc=True):
    total = ResourceVersion.get_versions_count(item_id, Resource.Type.ITEM)
    versions = ResourceVersion.get_all_versions(
        item_id, Resource.Type.ITEM,
        limit=limit, offset=offset, desc=desc
    )

    return total, versions


@item_versions_blueprint.route("", methods=["GET"])
@dict_response_deco
def item_version_display(item_id):
    op_info = parse_request_args(request)

    validate_for_item_modify(op_info.user_hash, item_id)

    total, versions = get_item_versions(item_id, limit=op_info.limit, offset=op_info.offset, desc=op_info.desc)
    return {
        "msg": "OK",
        "data": {
            "total": total,
            "versions": [{
                "id": version.version_id,
                "item_id": version.resource_id,
                "content": version.resource_content,
                "type": Item.Type.to_str(version.type),
                "visibility": version.resource_visibility,
                "updated_time": str(version.updated_at)
            } for version in versions]
        }
    }
