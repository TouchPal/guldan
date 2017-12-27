# -*- coding: utf-8 -*-
import logging
from redis.client import StrictRedis
import re
import json
from ..faulty_client import (
    FaultyClient,
    noop,
)

logger = logging.getLogger(__name__)

def parse_redis_url(url):
    m = re.match("redis://(.*?):(.*?)/(.*)", url)
    groups = m.groups()
    if not groups:
        raise Exception("invalid redis url:{}".format(url))

    return groups[0], int(groups[1]), int(groups[2])


def get_redis_client(url):
    host, port, db = parse_redis_url(url)
    return StrictRedis(
        host=host,
        port=port,
        db=db,
        socket_timeout=2,
        socket_connect_timeout=2
    )


class RedisManager(object):
    __metaclass__ = FaultyClient

    __faulted_methods__ = [
        ("store", noop),
    ]

    GREY_PULLER_NAMESPACE = "guldan@grey@puller"
    GREY_PULLER_KEY = "{ns}|{item_name}"
    GREY_PULLER_TIME_KEY = "{ns}|{item_name}@{ip}@grey@pull@time"
    NORMAL_PULLER_NAMESPACE = "guldan@normal@puller"
    NORMAL_PULLER_KEY = "{ns}|{item_name}"
    NORMAL_PULLER_TIME_KEY = "{ns}|{item_name}@{ip}@pull@time"

    LUA_PUT_SCRIPT = """
        local status = redis.call('sadd', KEYS[1], ARGV[1]) 
        if (status == 1 or status == 0) then
            if redis.call('ttl', KEYS[1]) == -1 then
                redis.call('expire', KEYS[1], 3600)
            end
        else
            return 0
        end
        if redis.call('set', KEYS[2], ARGV[2]) == 1 then
            if redis.call('ttl', KEYS[2]) == -1 then
                redis.call('expire', KEYS[2], 3600)
            end
            return 2
        end
        return 1
    """

    def __init__(self, redis_url):
        self.url = redis_url
        self.client = get_redis_client(redis_url)

    def store(self, dict_message):
        grey = bool(dict_message.get("grey"))
        if grey:
            self._store_grey(dict_message)
        else:
            self._store_normal(dict_message)

    def _generate_value_for_stats(self, dict_message):
        return json.dumps({
            "ip": dict_message.get("remote_addr", "unknown"),
            "cid": dict_message.get("cid", "unknown"),
            "cver": dict_message.get("cver", "unknown"),
            "iver": dict_message.get("iver", "unknown"),
            "lver": dict_message.get("lver", "unknown"),
            "ctype": dict_message.get("ctype", "unknown"),
            "puller_hash": dict_message.get("puller_hash", "unknown")
        })

    def _store_normal(self, dict_message):
        if not dict_message:
            return

        key = RedisManager.NORMAL_PULLER_KEY.format(
            ns=RedisManager.NORMAL_PULLER_NAMESPACE, item_name=dict_message["item_name"]
        )
        value = self._generate_value_for_stats(dict_message)
        puller_time_key = RedisManager.NORMAL_PULLER_TIME_KEY.format(
            ns=RedisManager.NORMAL_PULLER_NAMESPACE, item_name=dict_message.get("item_name", "unknown"),
            ip=dict_message.get("remote_addr", "unknown")
        )
        puller_time_value = dict_message.get("pull_time", "unknown")
        self.client.eval(RedisManager.LUA_PUT_SCRIPT, 2, key, puller_time_key, value, puller_time_value)

    def _store_grey(self, dict_message):
        if not dict_message:
            return
        item_name = dict_message.get("item_name", "unknown")
        key = RedisManager.GREY_PULLER_KEY.format(
            ns=RedisManager.GREY_PULLER_NAMESPACE, item_name=dict_message.get("item_name", "unknown")
        )
        value = self._generate_value_for_stats(dict_message)
        puller_time_key = RedisManager.GREY_PULLER_TIME_KEY.format(
            ns=RedisManager.GREY_PULLER_NAMESPACE, item_name=item_name,
            ip=dict_message.get("remote_addr", "unknown")
        )
        puller_time_value = dict_message.get("pull_time", "unknown")
        self.client.eval(RedisManager.LUA_PUT_SCRIPT, 2, key, puller_time_key, value, puller_time_value)
