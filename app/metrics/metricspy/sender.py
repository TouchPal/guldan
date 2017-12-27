# -*- coding: utf-8 -*-
import threading
import time
import logging
import socket
from .ringbuffer import RingBuffer

logger = logging.getLogger(__name__)


class MetricsSender(object):
    UDP_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __init__(self, metrics_addr, aggregate_count=1, ring_buffer_capacity=1000):
        self.metrics_addr = (metrics_addr[0], int(metrics_addr[1]))
        self.metrics_buffer = RingBuffer("GroupMetrics", max_length=ring_buffer_capacity)
        self.aggregate_count = aggregate_count
        t = threading.Thread(target=MetricsSender.metrics_aggregate_and_send, args=(
            self.metrics_buffer, self.metrics_addr, self.aggregate_count
        ))
        t.setDaemon(True)
        t.start()

    def write_metric(self, metric):
        self.metrics_buffer.offer(metric)

    @staticmethod
    def metrics_aggregate_and_send(ring_buffer, udp_addr, aggregate_count):
        while True:
            try:
                metrics_dict = MetricsSender.aggregate_metrics(ring_buffer, aggregate_count)
                if not metrics_dict:
                    time.sleep(1)
                else:
                    MetricsSender.send_metrics(metrics_dict, udp_addr)
            except:
                logger.exception("exec")
                time.sleep(1)

    @staticmethod
    def aggregate_metrics(ring_buffer, aggregate_count):
        aggregated_result = {}
        for i in xrange(aggregate_count):
            o = ring_buffer.pop()
            if not o:
                break
            else:
                uniq_name = o.get_uniq_name()
                old_value = aggregated_result.get(uniq_name, None)
                if not old_value:
                    aggregated_result[uniq_name] = o.value
                else:
                    aggregated_result[uniq_name] = old_value + o.value

        return aggregated_result

    @staticmethod
    def send_metrics(metrics_dict, udp_addr):
        for k, v in metrics_dict.items():
            MetricsSender.send(k, v, udp_addr)

    @staticmethod
    def send(name, value, udp_addr):
        message = "{}={}".format(name, value)

        if MetricsSender.UDP_SOCKET:
            MetricsSender.UDP_SOCKET.sendto(message, udp_addr)