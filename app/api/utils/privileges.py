# -*- coding: utf-8 -*-
from app.api.models.base import Resource
from app.api.models.privilege import Privilege
from app.api.models.user import User


def get_users_for_privileges(privileges):
    user_ids = set()
    for p in privileges:
        user_ids.add(p.user_id)

    users = User.get_by_ids(user_ids)
    user_dict = {}
    for u in users:
        user_dict[u.id] = u

    return user_dict


def construct_privileges_list(privileges, user_dict):
    priv_list = []
    for p in privileges:
        user = user_dict[p.user_id]
        priv_list.append({
            "id": p.id,
            "type": Privilege.Type.to_str(p.privilege_type),
            "user_id": user.id,
            "user_name": user.name
        })

    return priv_list


def get_privileges_for_resource(res_id, resource_type):
    privileges = Privilege.get_privileges_by_resource(res_id, resource_type)
    user_dict = get_users_for_privileges(privileges)

    return construct_privileges_list(privileges, user_dict)


def build_privilege_tree_under_user(user_hash):
    dict_tree = {}
    for name in Privilege.get_resource_names_under_user(user_hash):
        current_level = dict_tree
        for l in name[0].split("."):
            next_level = current_level.get(l, None)
            if next_level is None:
                current_level[l] = {}
                next_level = current_level[l]

            current_level = next_level

    return dict_tree


def filter_out_resources_under_user(resources, privilege_tree):
    filtered_resources = []
    if not privilege_tree:
        return [res for res in resources if res.visibility == Resource.Visibility.PUBLIC]

    for resource in resources:
        if resource.visibility == Resource.Visibility.PUBLIC:
            filtered_resources.append(resource)
            continue

        current_level = privilege_tree
        matched = True
        level = 0
        name_parts = resource.name.split(".")
        for name in name_parts:
            if name in current_level:
                current_level = current_level.get(name)
                level += 1
            elif len(current_level) == 0 and level > 0:
                break
            else:
                matched = False
                break
        if matched:
            filtered_resources.append(resource)

    return filtered_resources 


