# -*- coding: utf-8 -*-
import logging
import time

logger = logging.getLogger(__name__)
NOT_REGENERATED = object()


class Lock(object):
    def __init__(
        self,
        mutex,
        creator,
        value_and_created_fn,
        expiretime,
    ):
        self.mutex = mutex
        self.creator = creator
        self.value_and_created_fn = value_and_created_fn
        self.expiretime = expiretime

    def _is_expired(self, createdtime):
        """Return true if the expiration time is reached, or no
        value is available."""

        return not self._has_value(createdtime) or \
            (
                self.expiretime is not None and
                time.time() - createdtime > self.expiretime
            )

    def _has_value(self, createdtime):
        """Return true if the creation function has proceeded
        at least once."""
        return createdtime > 0

    def _enter(self):
        value_fn = self.value_and_created_fn

        try:
            value = value_fn()
            value, createdtime = value
        except:
            value = NOT_REGENERATED
            createdtime = -1

        generated = self._enter_create(createdtime)

        if generated is not NOT_REGENERATED:
            value, createdtime = generated
            return value
        elif value is NOT_REGENERATED:
            try:
                value, createdtime = value_fn()
                return value
            except:
                raise Exception("Generation function should "
                            "have just been called by a concurrent "
                            "thread.")

        return value

    def _enter_create(self, createdtime):
        if not self._is_expired(createdtime):
            return NOT_REGENERATED

        self.mutex.acquire()

        try:
            created, createdtime = self.creator()
        finally:
            self.mutex.release()

        return created, createdtime

    def __enter__(self):
        return self._enter()

    def __exit__(self, type, value, traceback):
        pass
