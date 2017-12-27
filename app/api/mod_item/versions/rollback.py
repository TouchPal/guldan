# -*- coding: utf-8 -*-
from flask import request
from . import item_versions_blueprint
from app.api.utils.request_util import parse_request
from app.api.mod_item.modify import item_modify
from app.api.mod_item.validate import validate_for_item_modify
from app.api.mod_item.utils import ensure_item
from app.api.models.base import Resource
from app.api.models.item import Item
from app.api.models.version import ResourceVersion
from app.exc import GulDanException
from app.api.utils.response import dict_response_deco


def parse_item_version_rollback_arguments(request):
    op_info = parse_request(request)

    version_id = request.args.get("version_id", None)
    if not version_id:
        raise GulDanException().with_code(400).with_message(u"请指定version_id")

    try:
        op_info.version_id = int(version_id)
        if op_info.version_id < 1:
            raise Exception()
    except:
        raise GulDanException().with_code(400).with_message(u"version_id参数应该是一个正整数")

    return op_info


def item_rollback(op_info, item_id):
    item = ensure_item(item_id)

    versions = ResourceVersion.get_versions_by_resource(item_id, Resource.Type.ITEM, [op_info.version_id])
    if not versions:
        raise GulDanException().with_code(404).with_message(
            u"找不到对应的版本，版本号({})".format(op_info.version_id)
        )

    version = versions[0]
    item_modify(
        item_id=item_id,
        item_data=version.resource_content,
        item_type=Item.Type.to_str(version.type),
        item_visibility=version.resource_visibility,
    )

    return {
        "id": item_id,
        "name": item.name,
        "type": version.resource_type,
        "visibility": Resource.Visibility.to_str(version.resource_visibility),
        "content": version.resource_content
    }


@item_versions_blueprint.route("/rollback", methods=["POST"])
@dict_response_deco
def item_version_rollback(item_id):
    ensure_item(item_id)
    op_info = parse_item_version_rollback_arguments(request)
    validate_for_item_modify(
        op_info.user_hash,
        item_id
    )

    rollback_info = item_rollback(op_info, item_id)

    return {
        "msg": "OK",
        "data": rollback_info
    }
