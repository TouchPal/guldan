#-*- coding: utf-8 -*-
from flask import request

from . import project_blueprint
from app.api.utils.decorators import (
    audit_create,
    privilege_deco_for_create,
)
from app.exc import GulDanException
from .validate import validate_user_for_proj_creation
from app.api.models.base import Resource
from app.api.models.org import Org
from app.api.models.project import Project
from app.api.utils import request_util, response


def parse_project_create_input_info(request):
    project_op_info = request_util.parse_request(request)

    http_body = project_op_info.http_body
    parent_id = request_util.item_check(http_body, "parent_id")
    project_name = request_util.item_check(http_body, "name")
    is_private = request_util.item_check(http_body, "private")

    project_op_info.set_parent_id(parent_id)
    project_op_info.set_resource_name(project_name)
    project_op_info.set_visibility(is_private)

    return project_op_info


@audit_create(resource_type=Resource.Type.PROJECT)
@privilege_deco_for_create(resource_type=Resource.Type.PROJECT)
def _create_project(
    parent_id=None, project_full_name=None, visibility=None
):
    project = Project.get_by_parent_and_name(parent_id, project_full_name)
    if project:
        raise GulDanException().with_message(u"项目({})已经在组织(id:{})中存在".format(
            project_full_name, parent_id
        )).with_code(409)

    project = Project(project_full_name, parent_id, visibility=visibility)
    Project.add(project)

    return project


def create_project_internal(project_name, parent_id=None, visibility=None):
    org = Org.get_by_id(parent_id)
    if not org:
        raise GulDanException().with_message(u"找不到组织(id:{})".format(parent_id)).with_code(404)

    project_full_name = "{}.{}".format(org.name, project_name)
    return _create_project(
        parent_id=parent_id,
        project_full_name=project_full_name,
        visibility=visibility
    )


@project_blueprint.route("", methods=["PUT"])
@response.dict_response_deco
def create_project():
    project_op_info = parse_project_create_input_info(request)

    validate_user_for_proj_creation(
        project_op_info.user_hash,
        project_op_info.parent_id
    )

    project = create_project_internal(
        project_op_info.resource_name,
        parent_id=project_op_info.parent_id,
        visibility=project_op_info.visibility
    )

    return {
        "msg": "OK",
        "data": project.to_dict()
    }
