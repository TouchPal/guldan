# -*- coding: utf-8 -*-
import logging
from flask import request, g, jsonify, make_response
from app import app
from app.db import db_manager
from app.exc import GulDanException, NotLoginException
from app.consts import (
    GULDAN_TOKEN_STR,
    GULDAN_SESSION_ID_STR,
    ITEM_VERSION_SEQUENCE_NAME,
    GREY_ITEM_VERSION_SEQUENCE_NAME,
)
from app.api.utils.validate import is_user_logged_in
from werkzeug.exceptions import HTTPException


logger = logging.getLogger(__name__)


def make_error_response(error, frontend_error_code):
    error_dict = error.to_dict()
    status_code = error_dict['status_code']
    del error_dict['status_code']

    error_dict["code"] = frontend_error_code
    response = jsonify(error_dict)
    response.status_code = status_code
    return response


def handle_db_session_when_exc():
    try:
        g.db_session.rollback()
    finally:
        g.db_session.close()
        g.DBSession.remove()


def handle_exc(error):
    handle_db_session_when_exc()
    return jsonify({"msg": u"系统内部错误", "code": -1}), 500


for cls in HTTPException.__subclasses__():
    app.register_error_handler(cls, handle_exc)


@app.errorhandler(GulDanException)
def handle_guldan_exception(error):
    handle_db_session_when_exc()
    return make_error_response(error, -1)


@app.errorhandler(NotLoginException)
def handle_notlogin_exception(error):
    handle_db_session_when_exc()
    return make_error_response(error, -2)


def init_admin_user():
    from app.api.mod_misc.register import create_user
    from app.api.models.user import User

    user = User.get_user_by_name("admin")
    if not user.name:
        create_user("admin", "123456")


def init_sequence_table():
    from app.api.models.sequence import SequenceDual

    item_version_sequence = SequenceDual.get_by_name(ITEM_VERSION_SEQUENCE_NAME)
    if not item_version_sequence:
        SequenceDual.add(SequenceDual(ITEM_VERSION_SEQUENCE_NAME, 100))

    grey_item_version_sequence = SequenceDual.get_by_name(GREY_ITEM_VERSION_SEQUENCE_NAME)
    if not grey_item_version_sequence:
        SequenceDual.add(SequenceDual(GREY_ITEM_VERSION_SEQUENCE_NAME, 100))


@app.before_first_request
def initial_setup():
    g.DBSession = db_manager.get_session("master")
    g.db_session = g.DBSession()

    try:
        init_admin_user()
        init_sequence_table()
        g.db_session.commit()
    except:
        logger.exception("db exc")
        g.db_session.rollback()
    finally:
        g.db_session.close()
        g.DBSession.remove()


@app.before_request
def add_db_session():
    if "/api/puller" in request.path:
        bind = "slave"
    else:
        bind = "master"

    g.DBSession = db_manager.get_session(bind)
    g.db_session = g.DBSession()


def get_user_info_from_request(req):
    session_id = req.cookies.get(GULDAN_SESSION_ID_STR, None)
    user_hash = req.cookies.get(GULDAN_TOKEN_STR, None)

    if not user_hash:
        raise GulDanException().with_code(400).with_message(u"登录信息不完整")

    if not session_id:
        session_id = req.headers.get(GULDAN_SESSION_ID_STR, None)
        if not session_id:
            raise GulDanException().with_code(400).with_message(u"登录信息不完整")

    return session_id, user_hash


LOGIN_CHECK_EXCLUDED_URL = [
    "/api/login",
    "/api/islogin",
    "/api/register",
]


def api_login_check():
    if request.path in LOGIN_CHECK_EXCLUDED_URL:
        return

    session_id, user_hash = get_user_info_from_request(request)
    try:
        user_info = is_user_logged_in(user_hash, session_id)
        user_id, user_name = user_info
    except GulDanException:
        raise
    except:
        raise NotLoginException().with_code(403).with_message(u"用户没有登录")

    g.user_id = user_id
    g.user_name = user_name
    g.user_hash = user_hash
    g.session_id = session_id


@app.before_request
def login_check():
    if request.path.startswith("/api/puller"):
        return

    if request.path.startswith("/api/"):
        api_login_check()


@app.after_request
def db_ending(response):
    db_session = g.get("db_session", None)
    if not db_session:
        return response

    try:
        if response.status_code == 200:
            db_session.commit()
    except:
        logger.exception("exc when db_ending")
        response = make_response(u"服务器内部错误", 500)
    finally:
        db_session.rollback()
        db_session.expunge_all()
        db_session.close()
        g.DBSession.remove()

    return response

