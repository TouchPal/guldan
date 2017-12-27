# -*- coding: utf-8 -*-
from app.exc import GulDanException
from app.api.models.base import Resource
from app.api.models.privilege import Privilege
from app.api.models.user import User


def can_user_view_org(org_id, user_hash):
    privilege = Privilege.get_privilege_by_user_and_resource(user_hash, org_id, Resource.Type.ORG)
    if privilege and privilege.privilege_type >= Privilege.Type.VIEWER:
        return True

    return False


def can_user_modify_org(org_id, user_hash):
    privilege = Privilege.get_privilege_by_user_and_resource(user_hash, org_id, Resource.Type.ORG)
    if privilege and privilege.privilege_type == Privilege.Type.MODIFIER:
        return True

    return False


def validate_for_user_modify_org(user_hash, org_id):
    if not can_user_modify_org(org_id, user_hash):
        user = User.get_user_by_user_hash(user_hash)
        raise GulDanException().with_message(u"用户({})没有权限修改组织(id:{})".format(
            user.name, org_id
        )).with_code(403)


def validate_for_user_view_org(user_hash, org_id):
    if not can_user_view_org(org_id, user_hash):
        user = User.get_user_by_user_hash(user_hash)
        raise GulDanException().with_message(u"用户({})没有权限查看组织(id:{})".format(
            user.name, org_id
        )).with_code(403)
