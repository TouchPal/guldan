# -*- coding: utf-8 -*-
import time
import functools
import socket
import logging
from .metricspy.groupmetrics import GroupMetrics
from app import load_app_config

logger = logging.getLogger(__name__)
metrics_clients = {}
HOSTNAME = socket.getfqdn()


class FakeGroupMetrics(object):
    def write_exc(self, name, value, tags=None):
        pass

    def write_count(self, name, value, tags=None):
        pass


def get_metrics_clent(measurement):
    try:
        metrics_client = metrics_clients.get(measurement, None)
        if not metrics_client:
            host_and_port = load_app_config().METRICS_URL.split(":")
            if len(host_and_port) != 2:
                metrics_client = FakeGroupMetrics()
            else:
                tags = {"hostname": HOSTNAME}
                metrics_client = GroupMetrics(
                    (host_and_port[0], int(host_and_port[1])),
                    measurement,
                    aggregate_count=1000,
                    ring_buffer_capacity=10000,
                    predefined_tags=tags
                )
            metrics_clients[measurement] = metrics_client

        return metrics_client
    except:
        logger.exception("exc when get metrics client")
        return FakeGroupMetrics()


def metrics(measurement, name, request=None):
    def metrics_deco(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            start_time = 0
            new_tags = {
                "remote_addr": request.remote_addr if request else "None"
            }
            try:
                start_time = time.time() * 1000
                result = func(*args, **kwargs)
                return result
            except:
                get_metrics_clent(measurement).write_exc(name, 1, tags=new_tags)
                raise
            finally:
                end_time = time.time() * 1000
                get_metrics_clent(measurement).write_count(name, 1, tags=new_tags)
                get_metrics_clent(measurement).write_count(name + ".cost", int(end_time - start_time), tags=new_tags)
    
        return inner

    return metrics_deco
