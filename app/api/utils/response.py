# -*- coding: utf-8 -*-
import functools
import logging

from flask import jsonify, make_response

from app.consts import GULDAN_VERSION_STR, GULDAN_TYPE_STR
from app.exc import GulDanException

logger = logging.getLogger(__name__)


def handle_puller_response(result):
    guldan_version = result[GULDAN_VERSION_STR]
    guldan_type = result[GULDAN_TYPE_STR]

    response = make_response(result['data'])

    response.headers[GULDAN_VERSION_STR] = guldan_version
    response.headers[GULDAN_TYPE_STR] = guldan_type

    return response


def response_deco(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except GulDanException as e:
            logger.exception(e.message)
            raise
        except:
            logger.exception("")
            raise GulDanException()

        return result

    return wrapper


def dict_response_deco(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except GulDanException as e:
            logger.exception(e.message)
            raise
        except:
            logger.exception("")
            raise GulDanException()

        try:
            if GULDAN_VERSION_STR in result:
                response = handle_puller_response(result)
            else:
                result["code"] = 0
                response = jsonify(**result)
        except:
            logger.exception("Exception")
            raise GulDanException()

        return response

    return wrapper
