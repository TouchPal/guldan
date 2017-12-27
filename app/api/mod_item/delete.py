# -*- coding: utf-8 -*-
from flask import request
from . import item_blueprint

from app.api.models.base import Resource
from app.api.models.item import Item
from app.api.utils import response
from app.api.utils.decorators import (
    audit_delete,
    privilege_deco_for_delete,
)
from app.api.mod_item.utils import ensure_item, invalidate_cache
from .validate import validate_for_item_modify
from .utils import parse_item_options_base
from .grey.delete import grey_item_delete


@audit_delete(resource_type=Resource.Type.ITEM)
@privilege_deco_for_delete(resource_type=Resource.Type.ITEM)
def item_delete(resource_id=None, resource_name=None, resource_visibility=None):
    invalidate_cache(resource_id, resource_name, resource_visibility)
    Item.delete(resource_id)
    return resource_id


@item_blueprint.route("/<int:item_id>", methods=["DELETE"])
@response.dict_response_deco
def delete_item(item_id):
    item = ensure_item(item_id)
    op_info = parse_item_options_base(request)

    validate_for_item_modify(
        op_info.user_hash,
        item_id
    )

    grey_item_delete(item_id)

    if not op_info.grey:
        item_delete(resource_id=item_id, resource_name=item.name, resource_visibility=item.visibility)

    return {
        "msg": "OK"
    }
