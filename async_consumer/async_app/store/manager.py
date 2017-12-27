# -*- coding: utf-8 -*-
import logging
from .redis_manager import RedisManager
import threading


logger = logging.getLogger(__name__)


class EmptyManager():
    def store(self, item_name, remote_addr):
        pass


empty_manager = EmptyManager()


class StoreManager(object):
    @staticmethod
    def create_manager(manager_url=None):
        if manager_url:
            if manager_url.startswith("redis"):
                return RedisManager(manager_url)

        return empty_manager


store_manager = None


def get_store_manager():
    return store_manager


def try_to_create_store_manager(url):
    import time
    while True:
        try:
            manager = StoreManager.create_manager(url)
        except:
            logger.error("exc when connect to store:{}".format(url))
            time.sleep(1)
        else:
            break

    global store_manager
    store_manager = manager


def init_store_manager(url):
    global store_manager
    try:
        store_manager = StoreManager.create_manager(url)
    except:
        logger.exception("exc when connect to store:{}".format(url))
        store_manager = empty_manager
        threading.Thread(target=try_to_create_store_manager, args=(url, )).start()

    return store_manager
