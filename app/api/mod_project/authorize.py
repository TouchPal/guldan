# -*- coding: utf-8 -*-
from flask import request, g

from app.exc import GulDanException
from .validate import validate_user_for_modify_project
from . import project_blueprint
from app.api.models.base import Resource
from app.api.models.item import Item
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
from .utils import ensure_project
from app.cache import cache
from app.api.mod_puller.pull import pull_item
from app.api.mod_puller.puller import ItemPuller


def parse_project_authorize_input_info(request):
    op_info = request_util.parse_request(request)
    http_body = op_info.http_body

    privilege_type = request_util.item_check(http_body, "type")
    target_user_id = request_util.item_check(http_body, "user_id")

    op_info.set_privilege_type(privilege_type)
    op_info.set_int_attr("target_user_id", target_user_id)

    return op_info


@audit_authorize_deco
def authorize_project_for_user(target_user=None, resource_id=None, privilege_type=None):
    if target_user.id == g.user_id:
        raise GulDanException().with_message(u"你不能为自己授权").with_code(403)

    if can_update_privilege_for_resource(target_user.user_hash, resource_id, Resource.Type.PROJECT, privilege_type):
        update_privilege_for_user(resource_id, Resource.Type.PROJECT, target_user.user_hash, privilege_type)
        return

    add_privilege_for_user(resource_id, Resource.Type.PROJECT, target_user.user_hash, privilege_type)


def disable_puller_cache_for_project(target_user, project_id):
    for item in Item.get_items_under_project(project_id):
        cache.delete_memoized(pull_item, ItemPuller(item.name), item.name, target_user.user_hash)


@project_blueprint.route("/<int:project_id>/authorize", methods=["POST"])
@response.dict_response_deco
def authorize_project(project_id):
    ensure_project(project_id)
    op_info = parse_project_authorize_input_info(request)
    target_user = ensure_user(op_info.target_user_id)
    validate_user_for_modify_project(
        op_info.user_hash,
        project_id
    )

    authorize_project_for_user(
        target_user=target_user,
        resource_id=project_id,
        privilege_type=op_info.privilege_type
    )

    if op_info.privilege_type != Privilege.Type.MODIFIER:
        disable_puller_cache_for_project(target_user, project_id)

    return {
        "msg": "OK"
    }


@audit_delete_privilege_deco
def delete_project_privilege_for_user(target_user=None, resource_id=None):
    if target_user.id == g.user_id:
        raise GulDanException().with_message(u"你不能删除自己的权限").with_code(409)

    Privilege.delete_privilege(target_user.user_hash, resource_id, Resource.Type.PROJECT)


@project_blueprint.route("/<int:project_id>/authorize/<int:user_id>", methods=["DELETE"])
@response.dict_response_deco
def delete_authorize(project_id, user_id):
    ensure_project(project_id)
    target_user = ensure_user(user_id)

    validate_user_for_modify_project(
        g.user_hash,
        project_id
    )

    delete_project_privilege_for_user(
        target_user=target_user,
        resource_id=project_id,
    )
    disable_puller_cache_for_project(target_user, project_id)

    return {
        "msg": "OK"
    }

