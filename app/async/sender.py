# -*- coding: utf-8 -*-
import logging
from kafka import get_kafka_manager

logger = logging.getLogger(__name__)


def send_dict(dict_message):
    try:
        get_kafka_manager().send_dict(dict_message)
    except:
        logger.exception("exc when send_dict")

