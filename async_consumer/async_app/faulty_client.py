# -*- coding: utf-8 -*-
import functools
import logging

logger = logging.getLogger(__name__)


class FaultyClient(type):
    @staticmethod
    def _deco(func, fallback):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except:
                logger.exception("exc when executing {}".format(func.__name__))
                return fallback(*args, **kwargs)

        return wrapper

    def __new__(self, name, bases, attrs):
        cls = type.__new__(self, name, bases, attrs)

        methods = cls.__faulted_methods__
        for method, fallback in methods:
            origin = getattr(cls, method)
            setattr(cls, method, self._deco(origin, fallback))
        return cls


def noop(*args, **kwargs):
    pass


def empty_list(*args, **kwargs):
    return []
