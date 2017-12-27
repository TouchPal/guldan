# -*- coding: utf-8 -*-
from flask import request, Blueprint
from app.api.utils.user import get_user_info_hash
from app.api.models.user import User
from app.api.utils import request_util, response

register_blueprint = Blueprint("register", __name__)


def create_user(target_user_name, target_user_password):
    secret_hash, user_hash = get_user_info_hash(target_user_name, target_user_password)
    User.add_with_check(target_user_name, secret_hash, user_hash)


def parse_user_register_input_info(request):
    http_body = request_util.retrieve_request_body(request)
    username = request_util.item_check(http_body, "name")
    password = request_util.item_check(http_body, "password")

    return username, password


@register_blueprint.route("/register", methods=["POST"])
@response.dict_response_deco
def user_register():
    user_name, user_password = parse_user_register_input_info(request)

    create_user(user_name, user_password)

    return {
        "msg": "OK"
    }
