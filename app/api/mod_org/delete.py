# -*- coding: utf-8 -*-
from flask import Blueprint, request
from . import org_blueprint

from app.api.models.project import Project
from app.api.models.org import Org
from app.api.models.base import Resource
from app.api.mod_project.delete import project_delete
from app.api.utils import request_util, response
from app.api.utils.decorators import (
    audit_delete,
    privilege_deco_for_delete,
)
from .validate import validate_for_user_modify_org
from .utils import ensure_org

org_delete_blueprint = Blueprint("org_delete", __name__)


def parse_org_delete_input_info(request):
    return request_util.parse_request(request)


@audit_delete(resource_type=Resource.Type.ORG)
@privilege_deco_for_delete(resource_type=Resource.Type.ORG)
def org_delete(resource_id=None):
    projects = Project.get_resources_under_parent_id(resource_id)
    for p in projects:
        project_delete(resource_id=p.id)

    Org.delete_by_id(resource_id)

    return resource_id


@org_blueprint.route("/<int:org_id>", methods=["DELETE"])
@response.dict_response_deco
def delete_org(org_id):
    ensure_org(org_id)
    org_op_info = parse_org_delete_input_info(request)

    validate_for_user_modify_org(
        org_op_info.user_hash,
        org_id
    )

    org_delete(resource_id=org_id, user_hash=org_op_info.user_hash)

    return {
        "msg": "OK"
    }
