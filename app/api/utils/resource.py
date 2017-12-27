# -*- coding: utf-8 -*-
from app.exc import GulDanException
from app.api.models.base import Resource
from app.api.models.item import Item
from app.api.models.org import Org
from app.api.models.privilege import Privilege
from app.api.models.project import Project
from app.api.models.user import User


def get_resource_model(resouce_type):
    if resouce_type == Resource.Type.ORG:
        return Org
    elif resouce_type == Resource.Type.PROJECT:
        return Project
    elif resouce_type == Resource.Type.ITEM:
        return Item
    else:
        return None


def build_full_resource_name(res_id, res_type):
    res_model = get_resource_model(res_type)
    res = res_model.get_by_id(res_id)
    if not res:
        raise GulDanException().with_message(u"找不到资源(id:{}, type:{})".format(
            res_id, res_type
        ))

    return res.name


def get_one_modifier(resource_type, resource_id):
    priv = Privilege.get_one_user_for_resource(resource_id, resource_type, Privilege.Type.MODIFIER)
    user_id = priv[0]
    user = User.get_by_id(user_id)
    if not user:
        raise GulDanException().with_code(404).with_message(u"找不到指定的用户")
    return {
        "user_id": user.id,
        "user_name": user.name
    }

