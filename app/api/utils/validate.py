# -*- coding: utf-8 -*-
from app.exc import *
from app.api.models.loginout import UserLogin
from app.api.models.user import User
from app.cache import cache


@cache.memoize()
def is_user_logged_in(user_hash, session_id):
    user = User.get_user_by_user_hash(user_hash)
    if not user:
        raise GulDanException().with_code(404).with_message(u"找不到用户")

    user_login = UserLogin.get_user_login_by_user_id(user.id)
    if not user_login.user_id:
        return False

    if not session_id or session_id == UserLogin.DEFAULT_SESSION_ID:
        return False

    if user_login.login_token == session_id:
        return user.id, user.name

    return False
