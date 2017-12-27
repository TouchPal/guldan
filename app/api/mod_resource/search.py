# -*- coding: utf-8 -*-
from flask import request

from . import resource_blueprint

from app.api.models.base import Resource
from app.api.utils import request_util, response
from app.api.utils.resource import get_resource_model
from app.exc import GulDanException


def parse_resource_search_info(request):
    op_info = request_util.parse_request(request)
    resource_name = request_util.item_check(request.args, "q")

    op_info.resource_name = resource_name

    return op_info


def get_resource_type(resource_name_splits):
    type_int = len(resource_name_splits)
    return Resource.Type.parse_from_int(type_int)


def resource_search_internal(resource_name):
    resource_name_splits = resource_name.split(".")
    if len(resource_name_splits) > 3:
        raise GulDanException().with_code(400).with_message(u"非法的资源名")

    resource_type = get_resource_type(resource_name_splits)
    resource_model = get_resource_model(resource_type)
    resource = resource_model.get_by_name(resource_name)
    if not resource:
        raise GulDanException().with_code(404).with_message(u"找不到资源")

    return [{
        "id": resource.id,
        "name": resource.name,
        "visibility": Resource.Visibility.to_str(resource.visibility)
    }]


@resource_blueprint.route("/search", methods=["GET"])
@response.dict_response_deco
def resource_search():
    op_info = parse_resource_search_info(request)

    resource = resource_search_internal(
        op_info.resource_name
    )

    return {
        "msg": "OK",
        "data": resource
    }

