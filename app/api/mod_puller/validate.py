# -*- coding: utf-8 -*-
from app.api.mod_item.validate import can_user_modify_item
from app.api.models.base import Resource
from app.api.models.privilege import Privilege


def get_privilege_for_item(user_hash, item_full_name):
    return Privilege.get_privilege_by_user_hash_and_resource_name(user_hash, item_full_name, Resource.Type.ITEM)


def is_item_public(visibility):
    return visibility == Resource.Visibility.PUBLIC


def can_user_pull_config(user_hash, item_full_name, item_info):
    if is_item_public(item_info["visibility"]):
        return True

    if not user_hash:
        return False

    if get_privilege_for_item(user_hash, item_full_name):
        return True

    return can_user_modify_item(item_info["id"], user_hash)

