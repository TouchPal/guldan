# -*- coding: utf-8 -*-
from flask import request

from app.api.mod_org.validate import validate_for_user_modify_org
from app.api.models.base import Resource
from app.api.models.org import Org
from app.api.utils import request_util, response
from app.api.utils.decorators import (
    audit_modify,
)
from app.exc import GulDanException
from . import org_blueprint
from .utils import ensure_org


def parse_org_modification_info(request):
    op_info = request_util.parse_request(request)
    http_body = op_info.http_body

    private = request_util.item_check(http_body, "private")
    lower_private = str(private).lower()
    if lower_private == "true":
        op_info.visibility = Resource.Visibility.PRIVATE
    elif lower_private == "false":
        op_info.visibility = Resource.Visibility.PUBLIC
    else:
        raise GulDanException().with_code(400).with_message(
                u"非法的可见性类型:{}".format(private)
        )

    return op_info


@audit_modify(resource_type=Resource.Type.ORG)
def org_modify(resource_id=None, visibility=None):
    return Org.update_visibility(
        resource_id,
        visibility
    )


@org_blueprint.route("/<int:org_id>", methods=["POST"])
@response.dict_response_deco
def modify_org(org_id):
    ensure_org(org_id)
    org_op_info = parse_org_modification_info(request)
    validate_for_user_modify_org(
        org_op_info.user_hash,
        org_id
    )

    org_modify(
        resource_id=org_id,
        visibility=org_op_info.visibility
    )

    return {
        "msg": "OK"
    }
