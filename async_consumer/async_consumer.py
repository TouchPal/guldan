# -*- coding: utf-8 -*-
from __future__ import print_function
import time
import signal
import sys
import subprocess
import threading
import logging
from logging.config import fileConfig
from async_app.config import get_configs
from async_app.async.kafka import init_kafka_manager
from async_app.async.consumer import consume_dict
from async_app.store.manager import init_store_manager, get_store_manager
from async_app.task import do_async_task
from async_app.metrics.client import metrics_client
from async_app.async.kafka import get_kafka_manager

subprocess.call(["mkdir", "-p", "/logs/guldan"])
fileConfig("logging_config.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

print = logger.info

STOPPED = False
consumer = None


def consume_messages():
    while True and not STOPPED:
        try:
            message = consume_dict()
            do_async_task(message, get_store_manager())
            metrics_client.write_count("message_count", 1)
        except:
            logger.exception("exc when consuming messages")
            metrics_client.write_exc("consume_exc", 1)


def exit_signal_handler(signal, frame):
    print("signal {} received, about to exit ...".format(signal))
    sys.exit(0)


def equip_signal():
    signal.signal(signal.SIGINT, exit_signal_handler)
    signal.signal(signal.SIGTERM, exit_signal_handler)


def heartbeat_producer():
    while True:
        try:
            get_kafka_manager().send_dict({
                "item_name": "test.test.test",
                "puller_hash": "guldan_puller_hash",
                "remote_addr": "127.0.0.1",
                "iver": "1",
                "cver": "0.1",
                "ctype": "fake",
                "cid": "1",
                "lver": "last_version",
                "pull_time": int(time.time())
            })
        except:
            logger.exception("exc in heartbeat producer")
        finally:
            time.sleep(1)


def start_heartbeat_producer():
    threading.Thread(target=heartbeat_producer).start()


def run():
    equip_signal()
    configs = get_configs()
    print("init kafka manager ...")
    init_kafka_manager(configs)
    print("start heartbeat producer ...")
    start_heartbeat_producer()
    print("init store manager ...")
    init_store_manager(configs.get("redis_url"))
    print("start to consume messages ...")
    consume_messages()


if __name__ == "__main__":
    run()
