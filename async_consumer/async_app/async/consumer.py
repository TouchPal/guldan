# -*- coding: utf-8 -*-
from kafka import get_kafka_manager


def consume_dict():
    return get_kafka_manager().consume_dict()
