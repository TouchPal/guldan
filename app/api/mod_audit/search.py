# -*- coding: utf-8 -*-

from flask import request

from . import audit_blueprint

from app.api.mod_audit.audit_target import generate_audit_target
from app.api.models.audit import Audit
from app.api.models.base import Resource
from app.api.models.user import User
from app.api.utils import request_util, response
from app.exc import GulDanException


def parse_audit_search_info(request):
    op_info = request_util.parse_request(request)

    limit = request_util.url_param_check(op_info, "limit")
    offset = request_util.url_param_check(op_info, "offset")
    op_info.resource_name = request_util.url_param_check(op_info, "q")

    op_info.set_limit(limit)
    op_info.set_offset(offset)

    return op_info


def generate_audit_response(audits, users_dict):
    result = []
    for audit in audits:
        result.append({
            "user_id": audit.user_id,
            "user_name": users_dict.get(audit.user_id, "unknown"),
            "op_name": Audit.Action.to_str(audit.action),
            "resource_id": audit.resource_id,
            "resource_type": Resource.Type.to_str(audit.resource_type),
            "resource_visibility": audit.resource_visibility,
            "content": audit.data,
            "type": audit.type,
            "op_time": str(audit.updated_at)
        })

    return result


def get_users_from_audits(audits):
    user_ids = {audit.user_id for audit in audits}
    users = User.get_by_ids(user_ids)
    result = {}
    for u in users:
        result[u.id] = u.name

    return result


@audit_blueprint.route("/search", methods=["GET"])
@response.dict_response_deco
def audit_search():
    op_info = parse_audit_search_info(request)

    audit_target = generate_audit_target(op_info.resource_name, op_info.user_hash)
    if not audit_target.can_view_audit():
        raise GulDanException().with_code(403).with_message(
            u"你没有权限查看该资源的操作权限({})".format(
                op_info.resource_name
            )
        )

    audits = audit_target.get_audit(offset=op_info.offset, limit=op_info.limit)
    total = audit_target.get_audit_count()
    users_dict = get_users_from_audits(audits)
    rows = generate_audit_response(audits, users_dict)
    return {
        "msg": "OK",
        "data": {
            "total": total,
            "audits": rows
        }
    }
