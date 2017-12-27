# -*- coding: utf-8 -*-
from flask import g
from app.exc import GulDanException
from app.api.mod_project.validate import can_user_view_project, can_user_modify_project
from app.api.models.base import Resource
from app.api.models.item import Item
from app.api.models.privilege import Privilege


def can_user_view_item(item_id, user_hash):
    item = Item.get_by_id(item_id)
    if not item:
        raise GulDanException().with_code(404).with_message(
            u"找不到配置项(id:{})".format(item_id)
        )

    if item.visibility == Resource.Visibility.PUBLIC:
        return True

    privilege = Privilege.get_privilege_by_user_and_resource(user_hash, item_id, Resource.Type.ITEM)
    if privilege and privilege.privilege_type >= Privilege.Type.VIEWER:
        return True

    project_id = Item.get_parent_id(item_id)
    return can_user_modify_project(project_id, user_hash)


def can_user_modify_item(item_id, user_hash):
    privilege = Privilege.get_privilege_by_user_and_resource(user_hash, item_id, Resource.Type.ITEM)
    if privilege and privilege.privilege_type == Privilege.Type.MODIFIER:
        return True

    project_id = Item.get_parent_id(item_id)
    return can_user_modify_project(project_id, user_hash)


def validate_for_item_modify(user_hash, item_id):
    if can_user_modify_item(item_id, user_hash):
        return

    raise GulDanException().with_message(u"用户({})不能修改配置项(id:{})".format(
        g.user_name, item_id
    )).with_code(403)


def validate_for_item_view(user_hash, item_id):
    if can_user_view_item(item_id, user_hash):
        return

    raise GulDanException().with_code(403).with_message(
        u"用户({})不能查看配置项(id:{})".format(g.user_name, item_id)
    )


def validate_for_item_creation(user_hash, project_id):
    if can_user_view_project(project_id, user_hash):
        return

    raise GulDanException().with_code(403).with_message(
        u"你没有权限在该项目(id:{})下创建配置项".format(project_id)
    )
