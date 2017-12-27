# -*- coding: utf-8 -*-
import logging
from .metricspy.groupmetrics import GroupMetrics
from async_app.config import HOSTNAME, load_app_config

logger = logging.getLogger(__name__)
metrics_clients = {}


class FakeGroupMetrics(object):
    def write_exc(self, name, value, tags=None):
        pass

    def write_count(self, name, value, tags=None):
        pass


def get_metrics_clent(measurement):
    try:
        metrics_client = metrics_clients.get(measurement, None)
        if not metrics_client:
            host_and_port = load_app_config().get("metrics_url").split(":")
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


metrics_client = get_metrics_clent("guldan_async_consumer")
