# -*- coding: utf-8 -*-
from flask import request

from . import users_blueprint
from app.api.models.user import User
from app.api.utils import request_util, response


def parse_user_search_op_info(request):
    op_info = request_util.parse_request(request)
    search_name = request_util.item_check(request.args, 'q')

    op_info.search_name = search_name

    return op_info


def search_user_internal(search_name):
    users = User.search_user_by_name(search_name)

    users_list = [{"id": u.id, "name": u.name} for u in users]
    return users_list


@users_blueprint.route("", methods=["GET"])
@response.dict_response_deco
def users_search():
    op_info = parse_user_search_op_info(request)

    search_result = search_user_internal(op_info.search_name)

    return {
        "msg": "OK",
        "data": search_result
    }
