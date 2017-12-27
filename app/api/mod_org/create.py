# -*- coding: utf-8 -*-
from flask import request

from app.api.utils.decorators import (
    audit_create,
    privilege_deco_for_create,
)
from app.consts import MAX_RESOURCE_NAME_LENGTH
from app.exc import GulDanException
from . import org_blueprint
from app.api.models.base import Resource
from app.api.models.org import Org
from app.api.utils import request_util, response


def parse_org_create_input_info(request):
    org_op_info = request_util.parse_request(request)
    http_body = org_op_info.http_body

    org_name = request_util.item_check(http_body, "name")
    is_private = request_util.item_check(http_body, "private")

    org_op_info.set_resource_name(org_name)
    org_op_info.set_visibility(is_private)

    return org_op_info


def is_existing_org(org_name):
    org = Org.get_by_name(org_name)
    if org:
        return True

    return False


@audit_create(resource_type=Resource.Type.ORG)
@privilege_deco_for_create(resource_type=Resource.Type.ORG)
def _create_org(
    org_name=None,
    visibility=None,
):
    org = Org(org_name, visibility=visibility)
    Org.add(org)
    return org


def create_org_internal(org_name, visibility=None):
    if len(org_name) > MAX_RESOURCE_NAME_LENGTH:
        raise GulDanException().with_code(403).with_message(
            u"组织名称最大是{}".format(MAX_RESOURCE_NAME_LENGTH)
        )

    if is_existing_org(org_name):
        raise GulDanException().with_message(u"组织（{}）已经存在".format(org_name)).with_code(409)

    return _create_org(
        org_name=org_name,
        visibility=visibility,
    )


@org_blueprint.route("", methods=["PUT"])
@response.dict_response_deco
def create_org():
    org_op_info = parse_org_create_input_info(request)

    org = create_org_internal(
        org_op_info.resource_name,
        visibility=org_op_info.visibility
    )

    return {
        "msg": "OK",
        "data": org.to_dict()
    }
