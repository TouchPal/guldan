# -*- coding: utf-8 -*-
import functools
import logging
import app

from flask import g

from app.api.models.base import Resource
from app.api.utils.resource import get_resource_model
from app.api.models.privilege import Privilege

logger = logging.getLogger(app.load_app_config().APP_NAME + '.audit')


def get_resource_type(func_name):
    if 'org' in func_name:
        return Resource.Type.ORG
    elif 'project' in func_name:
        return Resource.Type.PROJECT
    elif 'item' in func_name:
        return Resource.Type.ITEM
    else:
        return None


def audit(*args, **kwargs):
    try:
        resource_type = get_resource_type(kwargs['audit_func_name'])
        new_value = args[1]
        resource_id = kwargs.get('resource_id', None)

        if not resource_type or not new_value:
            return

        if not resource_id:
            msg_format = u"user(id:{user_id}, name:{user_name}) {op_str} {resource_type}(new_value:{new_value})"
        else:
            msg_format = u"user(id:{user_id}, name:{user_name}) {op_str} {resource_type}(id:{resource_id}, new_value:{new_value})"

        logger.info(msg_format.format(
            user_id=g.user_id,
            user_name=g.user_name,
            resource_type=Resource.Type.to_str(resource_type),
            new_value=new_value,
            op_str=kwargs['op_str'],
            resource_id=resource_id,
        ))
    except:
        logger.exception("error when doing audit")


def audit_delete(*args, **kwargs):
    try:
        resource_type = get_resource_type(kwargs['audit_func_name'])
        resource_model = get_resource_model(resource_type)
        resource_id = args[0]

        resource = resource_model.get_by_id_for_audit(resource_id)

        logger.info(
            "user(id:{user_id}, name:{user_name}) {op_str} {resource_type}(id:{resource_id}, name:{resource_name})".format(
                user_id=g.user_id,
                user_name=g.user_name,
                op_str="deleted",
                resource_type=Resource.Type.to_str(resource_type),
                resource_id=resource_id,
                resource_name=resource.name
            ))
    except:
        logger.exception("error when audit delete")


def audit_authorize(*args, **kwargs):
    try:
        resource_type = get_resource_type(kwargs['audit_func_name'])
        resource_model = get_resource_model(resource_type)
        target_user = kwargs["target_user"]
        resource_id = kwargs["resource_id"]
        privilege_type = kwargs["privilege_type"]
        resource = resource_model.get_by_id(resource_id)

        logger.info("user(id:{user_id}, name:{user_name}) "
                    "authorize privilege(type:{privilege_type}) on "
                    "{resource_type}(id:{resource_id}, name:{resource_name}) "
                    "to "
                    "user(id:{target_user_id}, name:{target_user_name})".format(
            user_id=g.user_id,
            user_name=g.user_name,
            privilege_type=Privilege.Type.to_str(privilege_type),
            resource_type=Resource.Type.to_str(resource_type),
            resource_id=resource_id,
            resource_name=resource.name,
            target_user_id=target_user.id,
            target_user_name=target_user.name
        ))

    except:
        logger.exception("error when audit authorize")


def audit_delete_privilege(*args, **kwargs):
    try:
        resource_type = get_resource_type(kwargs['audit_func_name'])
        resource_model = get_resource_model(resource_type)

        target_user = kwargs.get('target_user', None)
        resource_id = kwargs.get('resource_id', None)

        if not target_user:
            return

        resource = resource_model.get_by_id(resource_id)

        logger.info("user(id:{operator_id}, name:{operator_name}) "
                    "recycled privilege on "
                    "resource(id:{resource_id}, name:{resource_name}, type:{resource_type}) for "
                    "user(id:{target_user_id}, name:{target_user_name})".format(
            operator_id=g.user_id,
            operator_name=g.user_name,
            resource_id=resource_id,
            resource_name=resource.name,
            resource_type=Resource.Type.to_str(resource_type),
            target_user_id=target_user.id,
            target_user_name=target_user.name
        ))
    except:
        logger.exception("error when audit privilege")


def audit_create_deco(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        result = func(*args, **kwargs)

        audit(
            audit_func_name=func.__name__,
            op_str="created",
            resource_id=result.id,
            *args, **kwargs
        )

        return result

    return inner


def audit_modify_deco(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        result = func(*args, **kwargs)

        audit(
            audit_func_name=func.__name__,
            op_str="modified",
            resource_id=args[0],
            *args, **kwargs
        )

        return result

    return inner


def audit_delete_deco(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        result = func(*args, **kwargs)

        audit_delete(audit_func_name=func.__name__, op_str="deleted", *args, **kwargs)

        return result

    return inner


def audit_authorize_deco(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        result = func(*args, **kwargs)

        audit_authorize(audit_func_name=func.__name__, op_str="authorized", *args, **kwargs)

        return result

    return inner


def audit_delete_privilege_deco(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        result = func(*args, **kwargs)

        audit_delete_privilege(audit_func_name=func.__name__, *args, **kwargs)

        return result

    return inner
