# -*- coding: utf-8 -*-
import json
import logging
import re
from flask import g
from app.consts import GULDAN_TOKEN_STR, MAX_RESOURCE_NAME_LENGTH
from app.exc import GulDanException
from app.api.models.base import Resource
from app.api.models.item import Item
from app.api.models.privilege import Privilege
from .helper import valid_int
logger = logging.getLogger(__name__)

NAME_REGEX = "^[A-Za-z0-9-_]+$"
VISIBILITY_TYPES = ["true", "false"]


class UserOperationInfo(object):
    def __init__(self, session_id, user_hash):
        self.session_id = session_id
        self.user_hash = user_hash

    def set_int_attr(self, name, value):
        try:
            setattr(self, name, valid_int(value))
        except ValueError:
            raise GulDanException().with_code(400).with_message(u"{}应该是一个整数".format(name))

        if getattr(self, name) < 0:
            raise GulDanException().with_code(400).with_message(u"{}不应该小于0".format(name))

    def set_parent_id(self, parent_id):
        self.set_int_attr("parent_id", parent_id)

    def set_visibility(self, is_private):
        visibility_str = str(is_private).lower()
        if visibility_str not in VISIBILITY_TYPES:
            raise GulDanException().with_code(400).with_message(u"不支持的可见性类型({}), 合法的类型为: {}".format(
                is_private, ",".join(VISIBILITY_TYPES)
            ))

        if "true" == visibility_str:
            self.visibility = Resource.Visibility.PRIVATE
        else:
            self.visibility = Resource.Visibility.PUBLIC

    def set_item_type(self, item_type):
        if item_type is None:
            self.item_type = Item.Type.PLAIN
            return

        internal_type = Item.Type.to_type(item_type)
        if internal_type == Item.Type.INVALID:
            raise GulDanException().with_message(u"非法的配置项类型:{}".format(item_type)).with_code(400)

        self.item_type = internal_type

    def set_resource_name(self, name):
        if not name or not bool(re.match(NAME_REGEX, name)):
            raise GulDanException().with_message(u"资源名称({})不匹配正则表达式: {}".format(name, NAME_REGEX)).with_code(400)

        if len(name) > MAX_RESOURCE_NAME_LENGTH:
            raise GulDanException().with_code(403).with_message(
                u"名称最大长度是{}".format(MAX_RESOURCE_NAME_LENGTH)
            )

        self.resource_name = name

    def set_limit(self, limit):
        self.set_int_attr("limit", limit)

    def set_offset(self, offset):
        self.set_int_attr("offset", offset)

    def set_privilege_type(self, privilege_type):
        if not privilege_type:
            raise GulDanException().with_message(u"非法的授权类型:{}".format(privilege_type)).with_code(400)

        privilege_type_lower = privilege_type.lower()
        if privilege_type_lower == "modifier":
            self.privilege_type = Privilege.Type.MODIFIER
        elif privilege_type_lower == "viewer":
            self.privilege_type = Privilege.Type.VIEWER
        elif privilege_type_lower == "puller":
            self.privilege_type = Privilege.Type.PULLER
        else:
            raise GulDanException().with_message(u"非法的授权类型:{}".format(privilege_type)).with_code(400)


def retrieve_request_body(request):
    content = request.get_data()
    if not content:
        return None

    try:
        body = json.loads(content)
    except:
        raise GulDanException().with_code(400).with_message(u"非法的http body，应该为json")

    return body


def parse_request(req):
    session_id = g.get("session_id", None)
    user_hash = g.get("user_hash", None)

    op_info = UserOperationInfo(session_id, user_hash)
    for k, v in req.args.items():
        setattr(op_info, k.replace("-", "_"), v)

    op_info.http_body = retrieve_request_body(req)

    return op_info


def retrieve_puller_args(request):
    user_hash = request.headers.get(GULDAN_TOKEN_STR, None)
    return UserOperationInfo(None, user_hash)


def is_empty(item):
    if item is None:
        return True
    if isinstance(item, str):
        return not item

    return False


def url_param_check(info, param_name):
    if not hasattr(info, param_name):
        raise GulDanException().with_code(400).with_message(
            u"url参数 {} 没有提供".format(param_name)
        )

    return getattr(info, param_name)


def item_check(info, item_name):
    if not info:
        raise GulDanException().with_code(400).with_message(u"请求body不能为空")
    item = info.get(item_name, None)
    if is_empty(item):
        raise GulDanException().with_code(400).with_message(
            u"{}没有找到或不应该为空".format(item_name),
        )

    return item

