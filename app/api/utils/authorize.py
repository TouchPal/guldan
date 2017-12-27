# -*- coding: utf-8 -*-
from app.exc import GulDanException
from app.api.models.base import Resource
from app.api.models.privilege import Privilege
from app.api.models.user import User
from app.api.utils.resource import build_full_resource_name


def update_privilege_for_user(resource_id, resource_type, target_user_hash, privilege_type):
    Privilege.update_privilege_type(resource_id, resource_type, target_user_hash, privilege_type)


def add_privilege_for_user(resource_id, resource_type, target_user_hash, privilege_type):
    target_user = User.get_user_by_user_hash(target_user_hash)

    resource_name = build_full_resource_name(resource_id, resource_type)
    Privilege.add_with_check(resource_id, resource_name, resource_type, target_user.id, target_user.user_hash, privilege_type)


def can_update_privilege_for_resource(user_hash, resource_id, resource_type, target_privilege_type):
    resource_priv = Privilege.get_privilege_by_user_and_resource(user_hash, resource_id, resource_type)
    if resource_priv and resource_priv.resource_visibility == Resource.Visibility.PUBLIC:
        raise GulDanException().with_message(u"资源({})是公有的, 不需要授权".format(
            resource_priv.resource_name
        )).with_code(409)
    elif resource_priv:
        return True
    else:
        return False
