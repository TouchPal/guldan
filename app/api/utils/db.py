# -*- coding: utf-8 -*-
import functools
from flask import g


def with_db_flush(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        g.db_session.flush()
        return result

    return wrapper
