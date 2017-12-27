# -*- coding: utf-8 -*-
from flask import request

from . import project_blueprint

from app.api.models.base import Resource
from app.api.models.project import Project
from app.api.models.item import Item
from app.api.utils import request_util, response
from .validate import validate_user_for_modify_project
from app.api.utils.decorators import (
    audit_delete,
    privilege_deco_for_delete,
)
from app.api.mod_item.delete import item_delete


def parse_project_delete_input_info(request):
    return request_util.parse_request(request)


@audit_delete(resource_type=Resource.Type.PROJECT)
@privilege_deco_for_delete(resource_type=Resource.Type.PROJECT)
def project_delete(resource_id=None):
    items = Item.get_resources_under_parent_id(resource_id)
    item_ids = [item.id for item in items]

    for item_id in item_ids:
        item_delete(resource_id=item_id)

    Project.delete_by_id(resource_id)

    return resource_id


@project_blueprint.route("/<int:project_id>", methods=["DELETE"])
@response.dict_response_deco
def delete_project(project_id):
    project_op_info = parse_project_delete_input_info(request)

    validate_user_for_modify_project(
        project_op_info.user_hash,
        project_id
    )

    project_delete(resource_id=project_id, user_hash=project_op_info.user_hash)

    return {
        "msg": "OK"
    }
