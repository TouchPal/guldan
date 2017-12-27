# -*- coding: utf-8 -*-
import logging
from app.utils import parse_redis_url
from app import load_app_config
from redis import StrictRedis
import json
import itertools
import threading
from app.faulty_client import (
    FaultyClient,
    empty_list,
)

logger = logging.getLogger(__name__)

kv_manager = None


def create_redis_client(url):
    host, port, db = parse_redis_url(url)
    return StrictRedis(host=host, port=port, db=db, socket_connect_timeout=2, socket_timeout=2)


class KVManager(object):
    __metaclass__ = FaultyClient

    __faulted_methods__ = [
        ("get_item_grey_fetchers", empty_list),
        ("get_item_normal_fetchers", empty_list),
    ]

    GREY_PULLER_NAMESPACE = "guldan@grey@puller"
    GREY_PULLER_KEY = "{ns}|{item_name}"
    GREY_PULLER_TIME_KEY = "{ns}|{item_name}@{ip}@grey@pull@time"
    NORMAL_PULLER_NAMESPACE = "guldan@normal@puller"
    NORMAL_PULLER_KEY = "{ns}|{item_name}"
    NORMAL_PULLER_TIME_KEY = "{ns}|{item_name}@{ip}@pull@time"

    def __init__(self, kv_url):
        self.url = kv_url
        self.client = create_redis_client(kv_url)

    def get_item_grey_fetchers(self, item_name):
        puller_key = KVManager.GREY_PULLER_KEY.format(
            ns=KVManager.GREY_PULLER_NAMESPACE, item_name=item_name
        )
        puller_strs = self.client.smembers(puller_key)
        pullers = []
        puller_time_keys = []
        for puller_str in puller_strs:
            puller = json.loads(puller_str, encoding="utf-8")
            puller["grey"] = True
            pull_time_key = KVManager.GREY_PULLER_TIME_KEY.format(
                ns=KVManager.GREY_PULLER_NAMESPACE, item_name=item_name,
                ip=puller["ip"]
            )
            puller_time_keys.append(pull_time_key)
            pullers.append(puller)

        if puller_time_keys:
            pull_times = self.client.mget(puller_time_keys)
            for puller, puller_time in itertools.izip_longest(pullers, pull_times):
                puller["pull_time"] = puller_time

        return pullers

    def get_item_normal_fetchers(self, item_name):
        puller_key = KVManager.NORMAL_PULLER_KEY.format(
            ns=KVManager.NORMAL_PULLER_NAMESPACE, item_name=item_name
        )
        puller_strs = self.client.smembers(puller_key)
        pullers = []
        puller_time_keys = []
        for puller_str in puller_strs:
            puller = json.loads(puller_str)
            puller["grey"] = False
            pull_time_key = KVManager.NORMAL_PULLER_TIME_KEY.format(
                ns=KVManager.NORMAL_PULLER_NAMESPACE, item_name=item_name,
                ip=puller["ip"]
            )
            puller_time_keys.append(pull_time_key)
            pullers.append(puller)

        if puller_time_keys:
            pull_times = self.client.mget(puller_time_keys)
            for puller, puller_time in itertools.izip_longest(pullers, pull_times):
                puller["pull_time"] = puller_time

        return pullers


class FakeKVManager(object):
    def get_item_grey_fetchers(self, item_name):
        return []

    def get_item_normal_fetchers(self, item_name):
        return []


fake_kv_manager = FakeKVManager()


def try_to_connect_to_kv(url):
    import time
    while True:
        try:
            manager = KVManager(url)
        except:
            logger.error("error to connect to kv:{}".format(url))
            time.sleep(1)
        else:
            break

    global kv_manager
    kv_manager = manager


def get_kv_manager():
    global kv_manager
    if not kv_manager:
        redis_url = load_app_config().REDIS_URL
        try:
            kv_manager = KVManager(redis_url)
        except:
            logger.exception("exc when init KVManager, kv_url:{}".format(redis_url))
            kv_manager = fake_kv_manager
            threading.Thread(target=try_to_connect_to_kv, args=(redis_url,)).start()

    return kv_manager
