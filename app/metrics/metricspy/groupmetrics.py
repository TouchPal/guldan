# -*- coding: utf-8 -*-
import logging
import threading
from .metric import Metric
from .utils import merge_two_dicts
from .sender import MetricsSender

logger = logging.getLogger(__name__)


class GroupMetrics(object):
    """
    Send metrics using UDP, with grouping functionality.
    """

    INSTANCE_LOCK = threading.Lock()
    METRICS_SENDER = None

    def __init__(self, metrics_addr, name, aggregate_count=1, ring_buffer_capacity=1000, predefined_tags=None):
        """
        GroupMetrics will use an internal ring buffer to cache your metrics.
        A background thread will retrieve metrics from this ring buffer every 1 second, group metrics
        according to the `aggregate_count` and send metrics out through UDP.

        :param metrics_addr: the UDP address tuple, (host, port)
        :param name: the name of the this metrics, which is translated into measurement name in influxdb
        :param aggregate_count: the count of metrics in each grouping
        :param ring_buffer_capacity: the capacity for the ring buffer for metrics; this must be greater
                                     than the watched qps, or the metrics will not be accurate.
        :param predefined_tags: this is the predefined tags for your influxdb measurement.
        """
        self.name = name
        if predefined_tags:
            self.tags = predefined_tags
        else:
            self.tags = {}

        GroupMetrics.__init_metrics_sender(metrics_addr, aggregate_count, ring_buffer_capacity)

    @staticmethod
    def __init_metrics_sender(metrics_addr, aggregate_count, ring_buffer_capacity):
        with GroupMetrics.INSTANCE_LOCK:
            if not GroupMetrics.METRICS_SENDER:
                GroupMetrics.METRICS_SENDER = MetricsSender(
                    metrics_addr,
                    aggregate_count=aggregate_count,
                    ring_buffer_capacity=ring_buffer_capacity
                )

    def write_metrics(self, name, value, tags=None):
        if not isinstance(name, str):
            logger.error("name should be string")
            return
        if tags and not isinstance(tags, dict):
            logger.error("tags should be None or dict")
            return

        if not tags:
            tags = {}

        new_tags = merge_two_dicts(self.tags, tags)
        GroupMetrics.METRICS_SENDER.write_metric(Metric(self.name, new_tags, name, value))

    def write_count(self, name, value, tags=None):
        if not isinstance(value, int):
            logger.error("value should be integer")
            return

        self.write_metrics(name, value, tags=tags)

    def write_float(self, name, value, tags=None):
        if not isinstance(value, float):
            logger.error("value should be float")
            return

        self.write_metrics(name, value, tags=tags)

    def write_exc(self, name, value, tags=None):
        if not tags:
            tags = {}

        tags["exc"] = 1
        self.write_count(name, value, tags)
