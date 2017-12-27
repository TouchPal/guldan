# -*- coding: utf-8 -*-
from flask import request

from app.api.mod_project.validate import validate_user_for_modify_project
from app.api.models.base import Resource
from app.api.models.project import Project
from app.api.utils import request_util, response
from app.api.utils.decorators import audit_modify
from app.exc import GulDanException
from . import project_blueprint
from .utils import ensure_project


def parse_project_modification_info(request):
    op_info = request_util.parse_request(request)
    http_body = op_info.http_body

    private = request_util.item_check(http_body, "private")
    lower_private = str(private).lower()
    if lower_private == "true":
        op_info.visibility = Resource.Visibility.PRIVATE
    elif lower_private == "false":
        op_info.visibility = Resource.Visibility.PUBLIC
    else:
        raise GulDanException().with_code(400).with_message(
                u"非法的可见性类型:{}".format(http_body)
        )

    return op_info


@audit_modify(resource_type=Resource.Type.PROJECT)
def project_modify(resource_id=None, visibility=None):
    return Project.update_visibility(resource_id, visibility)


@project_blueprint.route("/<int:project_id>", methods=["POST"])
@response.dict_response_deco
def modify_project(project_id):
    ensure_project(project_id)
    project_op_info = parse_project_modification_info(request)
    validate_user_for_modify_project(
        project_op_info.user_hash,
        project_id
    )

    project_modify(
        resource_id=project_id,
        visibility=project_op_info.visibility
    )

    return {
        "msg": "OK"
    }
