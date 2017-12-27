# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify

from app.consts import GULDAN_SESSION_ID_STR, GULDAN_TOKEN_STR
from app.exc import GulDanException, NotLoginException
from app.api.models.loginout import UserLogin
from app.api.models.user import User
from app.api.utils import request_util, user
from app.api.utils.response import response_deco, dict_response_deco
from app.api.utils.validate import is_user_logged_in

login_blueprint = Blueprint("login", __name__)


def mark_user_as_login(user_id, login_token):
    return UserLogin.login_user_by_user_id(user_id, login_token)


def login_user(user_name, password):
    computed_secret_hash, computed_user_hash = user.get_user_info_hash(user_name, password)
    user_in_store = User.get_user_by_name(user_name)

    if user_in_store.secret_hash == computed_secret_hash:
        session_id = user.gen_session_id_for_user(user_name)
        new_token = mark_user_as_login(user_in_store.id, session_id)
        if new_token:
            session_id = new_token

        return {
            "session_id": session_id,
            "hash": user_in_store.user_hash,
            "name": user_name,
            "id": user_in_store.id,
        }
    else:
        raise GulDanException().with_code(400).with_message(u"用户名或密码不正确")


@login_blueprint.route("/login", methods=["POST"])
@response_deco
def login():
    login_info = request_util.retrieve_request_body(request)

    username = login_info.get("name", None)
    password = login_info.get("password", None)

    if not username or not password:
        raise GulDanException().with_code(400).with_message(u"登录信息不完整")

    login_result = login_user(username, password)

    http_response = jsonify({
        "code": 0,
        "msg": "OK",
        "data": login_result
    })
    http_response.set_cookie(GULDAN_SESSION_ID_STR, login_result['session_id'])
    http_response.set_cookie(GULDAN_TOKEN_STR, login_result['hash'])

    return http_response


@login_blueprint.route("/islogin", methods=["GET"])
@dict_response_deco
def islogin():
    session_id = request.cookies.get(GULDAN_SESSION_ID_STR, None)
    user_hash = request.cookies.get(GULDAN_TOKEN_STR, None)

    if not session_id:
        session_id = request.headers.get(GULDAN_SESSION_ID_STR, None)

    if not session_id or not user_hash:
        raise GulDanException().with_code(406).with_message(u"用户信息不完整")

    try:
        user_id, user_name = is_user_logged_in(user_hash, session_id)
    except:
        raise NotLoginException().with_code(406).with_message(u"用户没有登录")

    return {
        "msg": "OK",
        "data": {
            "session_id": session_id,
            "id": user_id,
            "name": user_name,
            "hash": user_hash
        }
    }
