# -*- coding: utf-8 -*-
import logging

from flask import Blueprint, g

from app.api.models.loginout import UserLogin
from app.api.utils.response import dict_response_deco
from app.api.utils.validate import is_user_logged_in
from app.cache import cache

logger = logging.getLogger("logout")

logout_blueprint = Blueprint("logout", __name__)


@logout_blueprint.route("/logout", methods=["POST"])
@dict_response_deco
def logout():
    UserLogin.logout_user_by_user_id(g.user_id, g.session_id)
    cache.delete_memoized(is_user_logged_in, g.user_hash, g.session_id)
    return {
        "msg": "OK"
    }
