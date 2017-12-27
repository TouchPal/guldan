# -*- coding: utf-8 -*-
from app.api.models.user import User
from app.exc import GulDanException


def ensure_user(user_id):
    user = User.get_by_id(user_id)
    if not user:
        raise GulDanException().with_code(404).with_message(u"找不到用户(id:{})".format(user_id))

    return user
