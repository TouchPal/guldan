# -*- coding: utf-8 -*-
from flask import g
from app.exc import GulDanException
from app.api.mod_org.validate import can_user_modify_org, can_user_view_org
from app.api.models.base import Resource
from app.api.models.privilege import Privilege
from app.api.models.project import Project
from .utils import ensure_project


def can_user_view_project(project_id, user_hash):
    project = ensure_project(project_id)

    if project.visibility == Resource.Visibility.PUBLIC:
        return True

    privilege = Privilege.get_privilege_by_user_and_resource(user_hash, project_id, Resource.Type.PROJECT)
    if privilege and privilege.privilege_type >= Privilege.Type.VIEWER:
        return True

    org_id = Project.get_parent_id(project_id)
    return can_user_modify_org(org_id, user_hash)


def can_user_modify_project(project_id, user_hash):
    privilege = Privilege.get_privilege_by_user_and_resource(user_hash, project_id, Resource.Type.PROJECT)
    if privilege and privilege.privilege_type == Privilege.Type.MODIFIER:
        return True

    org_id = Project.get_parent_id(project_id)
    return can_user_modify_org(org_id, user_hash)


def get_org_id(project_id):
    project = Project.get_by_id(project_id)
    if not project:
        raise GulDanException().with_message(u"找不到项目(id:{})".format(project_id)).with_code(404)

    return project.parent_id


def validate_user_for_proj_creation(user_hash, org_id):
    if not can_user_view_org(org_id, user_hash):
        raise GulDanException().with_message(u"用户({})没有权限修改组织(id:{})".format(
            g.user_name, org_id
        )).with_code(403)


def validate_user_for_modify_project(user_hash, project_id):
    if can_user_modify_project(project_id, user_hash):
        return

    org_id = Project.get_parent_id(project_id)
    if can_user_modify_org(org_id, user_hash):
        return

    raise GulDanException().with_code(403).with_message(
        u"用户({})没有权限修改项目(id:{})".format(g.user_name, project_id)
    )


def validate_user_for_view_project(user_hash, project_id):
    if can_user_view_project(project_id, user_hash):
        return

    org_id = Project.get_parent_id(project_id)
    if can_user_view_org(org_id, user_hash):
        return

    raise GulDanException().with_code(403).with_message(
        u"用户({})没有权限查看组织(id:{})".format(g.user_name, project_id)
    )
