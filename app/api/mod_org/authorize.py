# -*- coding: utf-8 -*-
from flask import request, g

from app.exc import GulDanException
from .validate import validate_for_user_modify_org
from . import org_blueprint
from app.api.models.base import Resource
from app.api.models.project import Project
from app.api.models.privilege import Privilege
from app.api.utils import request_util, response
from app.api.utils.audit import (
    audit_authorize_deco,
    audit_delete_privilege_deco,
)
from app.api.utils.authorize import (
    update_privilege_for_user,
    add_privilege_for_user,
    can_update_privilege_for_resource,
)
from app.api.mod_user.utils import ensure_user
from .utils import ensure_org
from app.api.mod_project.authorize import disable_puller_cache_for_project


def parse_org_authorize_input_info(request):
    op_info = request_util.parse_request(request)
    http_body = op_info.http_body

    privilege_type = request_util.item_check(http_body, "type")
    target_user_id = request_util.item_check(http_body, "user_id")

    op_info.set_privilege_type(privilege_type)
    op_info.set_int_attr("target_user_id", target_user_id)

    return op_info


@audit_authorize_deco
def authorize_org_for_user(target_user=None, resource_id=None, privilege_type=None):
    if target_user.id == g.user_id:
        raise GulDanException().with_message(u"你不能为自己授权").with_code(403)

    if can_update_privilege_for_resource(target_user.user_hash, resource_id, Resource.Type.ORG, privilege_type):
        update_privilege_for_user(resource_id, Resource.Type.ORG, target_user.user_hash, privilege_type)
        return

    add_privilege_for_user(resource_id, Resource.Type.ORG, target_user.user_hash, privilege_type)


def disable_puller_cache_for_org(target_user, org_id):
    for project in Project.get_projects_under_org(org_id):
        disable_puller_cache_for_project(target_user, project.id)


@org_blueprint.route("/<int:org_id>/authorize", methods=["POST"])
@response.dict_response_deco
def authorize_org(org_id):
    ensure_org(org_id)
    op_info = parse_org_authorize_input_info(request)
    target_user = ensure_user(op_info.target_user_id)
    validate_for_user_modify_org(
        op_info.user_hash,
        org_id
    )

    authorize_org_for_user(
        target_user=target_user,
        resource_id=org_id,
        privilege_type=op_info.privilege_type
    )

    if op_info.privilege_type != Privilege.Type.MODIFIER:
        disable_puller_cache_for_org(target_user, org_id)

    return {
        "msg": "OK"
    }


@audit_delete_privilege_deco
def delete_org_privilege_for_user(target_user=None, resource_id=None):
    if target_user.id == g.user_id:
        raise GulDanException().with_message(u"你不能删除自己的权限").with_code(409)

    Privilege.delete_privilege(target_user.user_hash, resource_id, Resource.Type.ORG)


@org_blueprint.route("/<int:org_id>/authorize/<int:user_id>", methods=["DELETE"])
@response.dict_response_deco
def delete_authorize(org_id, user_id):
    ensure_org(org_id)
    target_user = ensure_user(user_id)
    validate_for_user_modify_org(
        g.user_hash,
        org_id
    )

    delete_org_privilege_for_user(
        target_user=target_user,
        resource_id=org_id,
    )
    disable_puller_cache_for_org(target_user, org_id)

    return {
        "msg": "OK"
    }
