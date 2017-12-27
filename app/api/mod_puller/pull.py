# -*- coding: utf-8 -*-
import logging

from flask import request

from app.cache import cache

logger = logging.getLogger(__name__)
from . import puller_blueprint

from app.exc import GulDanException
from validate import can_user_pull_config
from app.consts import *
from app.api.utils import request_util
from app.api.utils.response import dict_response_deco
from app.metrics.client import metrics
from app.api.mod_puller.puller import create_puller
from async import create_async_sender
from app.cache.core import forced_update

METRICS_PULLER_MEASUREMENT = "api_puller"


@cache.memoize(timeout=3600, forced_update=forced_update)
def pull_item(puller, item_full_name, user_hash):
    logger.error("cache not hit, go to database, full_name:{}".format(item_full_name))

    item_info = puller.pull(item_full_name)

    if not can_user_pull_config(user_hash, item_full_name, item_info):
        raise GulDanException().with_message(u"你没有权限拉取配置，{}".format(
            item_full_name
        )).with_code(403)

    return item_info["content"], item_info["version_id"]


def parse_grey_option(op_info, url_args):
    grey_option = url_args.get("grey", None)
    if grey_option:
        grey_option_lower = grey_option.lower()
        if grey_option_lower == "true":
            op_info.grey = True
        elif grey_option_lower == "false":
            op_info.grey = False
        else:
            raise GulDanException().with_code(400).with_message(u"非法的灰度选项，它应该是个bool")
    else:
        op_info.grey = False

    return op_info


def parse_version_option(op_info, url_args):
    version_option = url_args.get("version", None)
    if version_option:
        try:
            version_id = int(version_option)
        except:
            raise GulDanException().with_code(400).with_message(u"非法的版本选项，它应该是个int")

        op_info.version_id = version_id
    else:
        op_info.version_id = None

    return op_info


def parse_string_option(op_info, url_args, target_str):
    str_option = url_args.get(target_str, None)
    if str_option:
        setattr(op_info, target_str, str_option)
    else:
        setattr(op_info, target_str, "unknown")

    return op_info


def parse_puller_args(request):
    op_info = request_util.retrieve_puller_args(request)
    op_info.remote_addr = request.remote_addr
    parse_grey_option(op_info, request.args)
    parse_version_option(op_info, request.args)
    parse_string_option(op_info, request.args, "cid")
    parse_string_option(op_info, request.args, "cver")
    parse_string_option(op_info, request.args, "ctype")
    parse_string_option(op_info, request.args, "lver")

    return op_info


@puller_blueprint.route("/<org_name>/<project_name>/<item_name>", methods=["GET"])
@dict_response_deco
@metrics(METRICS_PULLER_MEASUREMENT, "puller.request", request=request)
def pull_config(org_name, project_name, item_name):
    op_info = parse_puller_args(request)

    item_full_name = "{}.{}.{}".format(org_name, project_name, item_name)
    puller = create_puller(op_info, item_full_name)
    item_data, item_version = pull_item(puller, item_full_name, op_info.user_hash)

    op_info.item_version = item_version
    puller.send_async_message(op_info, request)

    return {
        "msg": "success",
        "data": item_data,
        GULDAN_VERSION_STR: item_version,
        GULDAN_TYPE_STR: "Plain"
    }

