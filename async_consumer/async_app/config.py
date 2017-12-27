# -*- coding: utf-8 -*-
import os
import logging
import socket

logger = logging.getLogger(__name__)
HOSTNAME = socket.getfqdn()
GULDAN_ASYNC_CONFIG_LIST = [
    "redis_url",
    "metrics_url",
    "kafka_brokers",
    "kafka_zk",
    "kafka_item_grey_topic",
    "kafka_consumer_group_name",
    "kafka_version",
]


def get_configs_from_env():
    configs = {}
    for config_name in GULDAN_ASYNC_CONFIG_LIST:
        configs[config_name] = os.getenv(config_name)

    return configs


def get_configs():
    try:
        return get_configs_from_env()
    except:
        logger.info("use default configs")
        return {
            "redis_url": "redis://127.0.0.1:16379/6",
            "metrics_url": "unset",
            "kafka_brokers": "127.0.0.1:10002",
            "kafka_zk": "127.0.0.1:2182",
            "kafka_item_grey_topic": "guldan_item_grey",
            "kafka_consumer_group_name": "guldan_item_grey_group",
            "kafka_version": "0.10.0.1"
        }


app_config = None


def load_app_config():
    global app_config
    if not app_config:
        app_config = get_configs()

    return app_config
