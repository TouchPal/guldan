# -*- coding: utf-8 -*-

import functools

from flask import request, render_template

from app.api.utils.validate import is_user_logged_in
from app.consts import GULDAN_SESSION_ID_STR, GULDAN_TOKEN_STR


def validate_user(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        user_hash = request.cookies.get(GULDAN_TOKEN_STR, None)
        session_id = request.cookies.get(GULDAN_SESSION_ID_STR, None)

        if not user_hash or not session_id:
            return render_template("404.html")

        if not is_user_logged_in(user_hash, session_id):
            return render_template("404.html")
        else:
            return func(*args, **kwargs)

    return inner
