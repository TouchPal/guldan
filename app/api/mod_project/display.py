# -*- coding: utf-8 -*-
from flask import request

from . import project_blueprint
from app.api.utils.privileges import (
    get_privileges_for_resource,
    build_privilege_tree_under_user,
    filter_out_resources_under_user,
)
from app.exc import GulDanException
from .validate import (
    can_user_view_project,
    can_user_modify_project,
)
from app.api.models.base import Resource
from app.api.models.item import Item
from app.api.models.privilege import Privilege
from app.api.utils import request_util, response
from app.api.utils.resource import get_one_modifier
from .utils import ensure_project


def get_items_list(project_id):
    items = Item.get_items_under_project(project_id)
    return [{
        "id": item.id,
        "name": item.name
    }for item in items]


def filter_items_under_user(items, user_hash):
    privilege_tree = build_privilege_tree_under_user(user_hash)
    return filter_out_resources_under_user(items, privilege_tree)


def can_not_view_response(project_id):
    modifier = get_one_modifier(Resource.Type.PROJECT, project_id)

    raise GulDanException().with_code(403).with_message(u"你没有权限查看该项目, 可以向{}申请权限".format(
        modifier["user_name"]
    ))


def separate_public_and_private_items(items):
    public_items = []
    private_items = []
    for item in items:
        if item.visibility == Resource.Visibility.PUBLIC:
            public_items.append(item)
        else:
            private_items.append(item)

    return public_items, private_items


def get_items_that_user_can_see(user_hash, project_id):
    items = Item.get_items_under_project(project_id)
    public_items, private_items = separate_public_and_private_items(items)

    privileges = Privilege.get_privileges_under_user(
        user_hash, Resource.Type.ITEM,
        [item.id for item in private_items]
    )

    items_list = [item.to_dict() for item in public_items]
    for p in privileges:
        items_list.append({
            "id": p.resource_id,
            "name": p.resource_name
        })

    return items_list


def get_items_for_project(project_id):
    items = Item.get_items_under_project(project_id)
    return [item.to_dict() for item in items]


@project_blueprint.route("/<int:project_id>", methods=['GET'])
@response.dict_response_deco
def get_items_under_project(project_id):
    project = ensure_project(project_id)
    op_info = request_util.parse_request(request)
    user_hash = op_info.user_hash

    project_info = project.to_dict()
    if can_user_modify_project(project_id, user_hash):
        items_dict = get_items_list(project_id)
        privileges_dict = get_privileges_for_resource(project_id, Resource.Type.PROJECT)

        project_info["privileges"] = privileges_dict
        project_info["items"] = items_dict
        project_info["access_mode"] = "modifier"
        return {
            "msg": "OK",
            "data": project_info
        }
    else:
        if can_user_view_project(project_id, user_hash):
            project_info["items"] = get_items_for_project(project_id)
            project_info["access_mode"] = "viewer"
            return {
                "msg": "OK",
                "data": project_info
            }

        items_list = get_items_that_user_can_see(user_hash, project_id)
        if items_list:
            project_info["items"] = items_list
            project_info["access_mode"] = "other"
            return {
                "msg": "OK",
                "data": project_info
            }

        return can_not_view_response(project_id)
