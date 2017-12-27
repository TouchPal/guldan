# -*- coding: utf-8 -*-
from flask import request
from app.api.utils.request_util import parse_request
from app.api.utils import response
from app.api.mod_item import item_blueprint
from app.api.mod_item.utils import ensure_item
from app.api.mod_item.validate import validate_for_item_modify
from app.api.mod_item.modify import item_modify
from .utils import ensure_grey_item, invalidate_cache_for_grey


def parse_grey_item_full_deploy_arguments(request):
    op_info = parse_request(request)
    return op_info


def item_full_deploy(resource_id=None, item=None, grey_item=None):
    invalidate_cache_for_grey(item.id, item.name, grey_item.item_visibility)
    item_modify(
        item_id=resource_id, item_data=grey_item.item_data, item_type=grey_item.item_type,
        item_visibility=grey_item.item_visibility, in_grey=False
    )


@item_blueprint.route("/<int:item_id>/upgrade", methods=["POST"])
@response.dict_response_deco
def full_deploy_item(item_id):
    item = ensure_item(item_id)
    grey_item = ensure_grey_item(item_id)
    op_info = parse_grey_item_full_deploy_arguments(request)

    validate_for_item_modify(
        op_info.user_hash,
        item_id
    )

    item_full_deploy(resource_id=item_id, item=item, grey_item=grey_item)

    return {
        "msg": "OK"
    }
