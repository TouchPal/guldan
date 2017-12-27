# -*- coding: utf-8 -*-
from flask import request

from app.api.mod_item.validate import validate_for_item_creation
from app.api.utils.decorators import (
    audit_create,
    privilege_deco_for_create,
)
from app.consts import ITEM_VERSION_SEQUENCE_NAME
from app.exc import GulDanException
from . import item_blueprint
from app.api.models.base import Resource
from app.api.models.item import Item
from app.api.models.project import Project
from app.api.models.sequence import SequenceDual
from app.api.utils import request_util, response
from .utils import parse_item_options_base
from .grey.create import grey_item_create


def get_item_info(item_id):
    item = Item.get_by_id(item_id)
    if not item:
        raise GulDanException().with_message(u"找不到配置项, id:{}".format(item_id)).with_code(404)

    return item.to_dict()


def parse_item_create_argument(request):
    op_info = parse_item_options_base(request)
    http_body = op_info.http_body

    item_name = request_util.item_check(http_body, "name")
    item_type = request_util.item_check(http_body, "type")
    parent_id = request_util.item_check(http_body, "parent_id")
    is_private = request_util.item_check(http_body, "private")
    item_data = http_body.get("content", None)

    op_info.item_data = item_data
    op_info.set_resource_name(item_name)
    op_info.set_parent_id(parent_id)
    op_info.set_visibility(is_private)
    op_info.set_item_type(item_type)

    return op_info


@audit_create(resource_type=Resource.Type.ITEM)
@privilege_deco_for_create(resource_type=Resource.Type.ITEM)
def _create_item(
    parent_id=None, item_full_name=None,
    item_data=None, item_type=None, visibility=None
):
    item = Item.get_item_under_project(parent_id, item_full_name)
    if item:
        raise GulDanException().with_message(u"配置项（{}）已经存在".format(item_full_name)).with_code(409)

    with SequenceDual.select_for_update(ITEM_VERSION_SEQUENCE_NAME) as sequence:
        item = Item(item_full_name, parent_id, item_data, item_type, visibility=visibility, version_id=sequence.value)
        Item.add(item)

    return item


def create_item_internal(item_name, item_data, item_type, parent_id=None, visibility=None):
    project = Project.get_by_id(parent_id)
    if not project:
        raise GulDanException().with_message(u"找不到项目(id:{})".format(parent_id)).with_code(404)

    item_full_name = "{}.{}".format(project.name, item_name)
    return _create_item(
        parent_id=parent_id,
        item_full_name=item_full_name,
        item_data=item_data,
        item_type=item_type,
        visibility=visibility
    )


@item_blueprint.route("", methods=["PUT"])
@response.dict_response_deco
def create_item():
    op_info = parse_item_create_argument(request)

    validate_for_item_creation(
        op_info.user_hash,
        op_info.parent_id
    )

    if op_info.grey:
        item = grey_item_create(op_info)
    else:
        item = create_item_internal(
            op_info.resource_name,
            op_info.item_data,
            op_info.item_type,
            parent_id=op_info.parent_id,
            visibility=op_info.visibility
        )

    return {
        "msg": "OK",
        "data": item.to_dict(),
    }
