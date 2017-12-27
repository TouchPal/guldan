# -*- coding: utf-8 -*-
from flask import request, g

from app.exc import GulDanException
from .validate import validate_for_item_modify
from . import item_blueprint
from app.api.models.base import Resource
from app.api.models.privilege import Privilege
from app.api.utils import request_util, response
from app.api.utils.audit import (
    audit_authorize_deco,
    audit_delete_privilege_deco,
)
from app.api.utils.authorize import (
    update_privilege_for_user,
    add_privilege_for_user,
    can_update_privilege_for_resource
)
from app.api.mod_user.utils import ensure_user
from app.api.mod_puller.pull import pull_item
from app.api.mod_puller.puller import ItemPuller
from app.cache import cache
from .utils import parse_item_options_base, ensure_item


def parse_item_authorize_input_info(request):
    op_info = parse_item_options_base(request)
    http_body = op_info.http_body

    privilege_type = request_util.item_check(http_body, "type")
    target_user_id = request_util.item_check(http_body, "user_id")

    op_info.set_privilege_type(privilege_type)
    op_info.set_int_attr("target_user_id", target_user_id)

    return op_info


@audit_authorize_deco
def authorize_item_for_user(target_user=None, resource_id=None, privilege_type=None):
    if target_user.id == g.user_id:
        raise GulDanException().with_message(u"你不能为自己授权").with_code(409)

    if can_update_privilege_for_resource(target_user.user_hash, resource_id, Resource.Type.ITEM, privilege_type):
        update_privilege_for_user(resource_id, Resource.Type.ITEM, target_user.user_hash, privilege_type)
        return

    add_privilege_for_user(resource_id, Resource.Type.ITEM, target_user.user_hash, privilege_type)


@item_blueprint.route("/<int:item_id>/authorize", methods=["POST"])
@response.dict_response_deco
def authorize_item(item_id):
    ensure_item(item_id)
    op_info = parse_item_authorize_input_info(request)
    if op_info.grey:
        raise GulDanException().with_code(403).with_message(u"灰度的配置项不支持授权操作")

    target_user = ensure_user(op_info.target_user_id)
    validate_for_item_modify(
        op_info.user_hash,
        item_id
    )

    authorize_item_for_user(
        target_user=target_user,
        resource_id=item_id,
        privilege_type=op_info.privilege_type
    )

    return {
        "msg": "OK"
    }


@audit_delete_privilege_deco
def delete_item_privilege_for_user(target_user=None, resource_id=None):
    if target_user.id == g.user_id:
        raise GulDanException().with_message(u"你不能删除自己的权限").with_code(409)

    Privilege.delete_privilege(target_user.user_hash, resource_id, Resource.Type.ITEM)

    item = ensure_item(resource_id)
    cache.delete_memoized(pull_item, ItemPuller(item.name), item.name, target_user.user_hash)


def parse_item_authorize_delete(req):
    return parse_item_options_base(request)


@item_blueprint.route("/<int:item_id>/authorize/<int:user_id>", methods=["DELETE"])
@response.dict_response_deco
def delete_authorize(item_id, user_id):
    target_user = ensure_user(user_id)
    op_info = parse_item_authorize_delete(request)

    if op_info.grey:
        raise GulDanException().with_code(403).with_message(u"灰度的配置项不支持授权操作")

    validate_for_item_modify(
        op_info.user_hash,
        item_id
    )

    delete_item_privilege_for_user(
        target_user=target_user,
        resource_id=item_id,
    )

    return {
        "msg": "OK"
    }
