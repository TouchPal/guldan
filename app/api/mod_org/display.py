# -*- coding: utf-8 -*-
from flask import request

from app.exc import GulDanException
from .validate import can_user_modify_org, can_user_view_org
from . import org_blueprint
from app.api.models.base import Resource
from app.api.models.org import Org
from app.api.models.privilege import Privilege
from app.api.models.project import Project
from app.api.utils import request_util, response
from app.api.utils.privileges import (
    get_privileges_for_resource,
)
from app.api.utils.resource import get_one_modifier
from .utils import ensure_org


def get_project_dict(projects):
    result = {}
    for p in projects:
        result[p.id] = p.to_dict()

    return result


def get_all_projects_list(org_id):
    projects = Project.get_projects_under_org(org_id)
    return [p.to_dict() for p in projects]


def _generate_org_list(name_set):
    orgs = Org.get_by_names(name_set)

    org_list = []
    for org in orgs:
        org_list.append({"id": org.id, "name": org.name})

    return org_list
    

def get_user_orgs(user_hash):
    privileges = Privilege.get_privileges_under_user_for_resource(
        user_hash,
        [Resource.Type.ORG, Resource.Type.PROJECT, Resource.Type.ITEM],
        [Privilege.Type.MODIFIER, Privilege.Type.VIEWER]
    )

    org_name_set = set()
    for p in privileges:
        org_name_set.add(p.resource_name.split(".")[0])

    return _generate_org_list(org_name_set)


@org_blueprint.route("", methods=["GET"])
@response.dict_response_deco
def get_orgs_under_user():
    op_info = request_util.parse_request(request)

    orgs_list = get_user_orgs(op_info.user_hash)
    return {
        "msg": "OK",
        "data": orgs_list
    }


def can_not_view_response(org_id):
    modifier = get_one_modifier(Resource.Type.ORG, org_id)

    raise GulDanException().with_code(403).with_message(u"你没有权限查看该项目, 可以向{}申请权限".format(
        modifier["user_name"]
    ))


def separate_public_and_private_projects(projects):
    public_projects = []
    private_projects = []

    for p in projects:
        if p.visibility == Resource.Visibility.PUBLIC:
            public_projects.append(p)
        else:
            private_projects.append(p)

    return public_projects, private_projects


def get_projects_that_user_can_see(user_hash, org_id):
    projects = Project.get_projects_under_org(org_id)
    public_projects, private_projects = separate_public_and_private_projects(projects)
    projects_list = [p.to_dict() for p in public_projects]

    org = Org.get_by_id(org_id)
    privileges = Privilege.get_privileges_by_name_prefix(org.name + ".", user_hash)
    project_names_under_user = {p.resource_name.split(".")[1] for p in privileges}
    for p in filter(lambda p : p.name.split(".")[1] in project_names_under_user, private_projects):
        projects_list.append(p.to_dict())

    return projects_list


@org_blueprint.route("/<int:org_id>", methods=["GET"])
@response.dict_response_deco
def get_org_by_id(org_id):
    org = ensure_org(org_id)
    op_info = request_util.parse_request(request)
    user_hash = op_info.user_hash

    org_info = org.to_dict()
    if can_user_modify_org(org_id, user_hash):
        projects_list = get_all_projects_list(org_id)
        privs = get_privileges_for_resource(org_id, Resource.Type.ORG)

        org_info["privileges"] = privs
        org_info["projects"] = projects_list
        org_info["access_mode"] = "modifier"
        return {
            "msg": "OK",
            "data": org_info
        }
    else:
        if can_user_view_org(org_id, user_hash):
            org_info["projects"] = get_all_projects_list(org_id)
            org_info["access_mode"] = "viewer"
            return {
                "msg": "OK",
                "data": org_info
            }

        projects_list = get_projects_that_user_can_see(user_hash, org_id)
        if projects_list:
            org_info["projects"] = projects_list
            org_info["access_mode"] = "other"
            return {
                "msg": "OK",
                "data": org_info
            }

        return can_not_view_response(org_id)

