# -*- coding: utf-8 -*-
from flask import request, g
from . import user_blueprint

from app.api.models.user import User
from app.api.utils import request_util, response
from app.api.utils.user import get_user_info_hash
from app.exc import GulDanException
from .utils import ensure_user


def parse_user_modify_input_info(request):
    user_op_info = request_util.parse_request(request)
    http_body = user_op_info.http_body

    new_password = request_util.item_check(http_body, "new_password")

    user_op_info.new_password = new_password

    return user_op_info


def reset_user(target_user, new_password):
    secret_hash, user_hash = get_user_info_hash(target_user.name, new_password)

    User.update_user(target_user.id, target_user.name, secret_hash)


@user_blueprint.route("/<int:user_id>", methods=["POST"])
@response.dict_response_deco
def user_modify(user_id):
    user = ensure_user(user_id)
    user_op_info = parse_user_modify_input_info(request)

    if g.user_name != "admin" and user.user_hash != user_op_info.user_hash:
        raise GulDanException().with_code(403).with_message(u"你只能修改自己的信息")

    reset_user(
        user,
        user_op_info.new_password
    )

    return {
        "msg": "OK"
    }
