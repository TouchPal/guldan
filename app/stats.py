# -*- coding: utf-8 -*-
import time
import socket
from app import load_app_config


class Stats(object):
    STATS_INTERVAL = 10

    def __init__(self):
        self.num_of_transactions = 0
        self.num_of_queries = 0
        self.start_time = time.time()

    def reset(self):
        self.num_of_queries = 0
        self.num_of_transactions = 0
        self.start_time = time.time()

    def update_transaction_num(self):
        if time.time() > self.start_time + Stats.STATS_INTERVAL:
            self.reset()

        self.num_of_transactions += 1

    def update_query_num(self):
        if time.time() > self.start_time + Stats.STATS_INTERVAL:
            self.reset()

        self.num_of_queries += 1

    def get_stats(self):
        current_time = time.time()
        qps = self.num_of_queries / (current_time - self.start_time)
        tps = self.num_of_transactions / (current_time - self.start_time)

        hostname = socket.gethostname()
        port = load_app_config().LISTENING_PORT

        return {
            'qps': qps,
            'tps': tps,
            'hostname': hostname,
            'port': port
        }


sys_stats = Stats()
