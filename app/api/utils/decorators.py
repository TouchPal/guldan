# -*- coding: utf-8 -*-
import functools
from flask import g
from app.api.models.audit import Audit
from app.api.models.privilege import Privilege
from app.api.models.base import Resource
from app.api.models.version import ResourceVersion
from app.api.utils.resource import get_resource_model


def audit_create(resource_type=None):
    assert resource_type is not None, "resource_type cannot be None"

    def wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            resource = func(*args, **kwargs)

            Audit.add(
                Audit(g.user_id, Audit.Action.CREATE, resource.id, resource_type, resource.current_version_id)
            )
            return resource

        return inner

    return wrapper


def privilege_deco_for_create(resource_type=None):
    assert resource_type is not None, "resource_type cannot be None"

    def wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            resource = func(*args, **kwargs)
            Privilege.add_with_check(
                resource.id, resource.name, resource_type,
                g.user_id, g.user_hash, Privilege.Type.MODIFIER, kwargs["visibility"]
            )
            return resource

        return inner
    return wrapper


def audit_delete(resource_type=None):
    assert resource_type is not None, "resource_type cannot be None"

    def wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            resource_id = func(*args, **kwargs)

            Audit.add(
                Audit(g.user_id, Audit.Action.DELETE, resource_id, resource_type, resource_id)
            )
            return resource_id

        return inner
    return wrapper


def privilege_deco_for_delete(resource_type=None):
    assert resource_type is not None, "resource_type cannot be None"

    def wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            result = func(*args, **kwargs)
            resource_id = kwargs["resource_id"]
            Privilege.delete(resource_id, resource_type)
            return result

        return inner

    return wrapper


def audit_modify(resource_type=None):
    assert resource_type is not None, "resource_type cannot be None"

    def wrapper(func):
        def record_version(resource, resource_type):
            if resource_type == Resource.Type.ITEM:
                resource_content = resource.data
                type_within_resource = resource.type
            else:
                resource_content = ""
                type_within_resource = 0

            ResourceVersion.add(
                ResourceVersion(
                    resource.id,
                    resource_type,
                    resource.current_version_id,
                    resource_content,
                    resource.visibility,
                    type=type_within_resource
            ))

        @functools.wraps(func)
        def inner(*args, **kwargs):
            resource_id = kwargs.get("resource_id", None)
            assert resource_id is not None, "modify function must have resource_id keyword argument"

            resource_model = get_resource_model(resource_type)
            origin_resource = resource_model.get_by_id(resource_id)
            record_version(origin_resource, resource_type)

            result = func(*args, **kwargs)

            new_resource = resource_model.get_by_id(resource_id)

            Audit.add(
                Audit(g.user_id, Audit.Action.MODIFY, resource_id, resource_type, new_resource.current_version_id)
            )
            return result
        return inner
    return wrapper

