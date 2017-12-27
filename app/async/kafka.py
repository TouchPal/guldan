# -*- coding: utf-8 -*-
import logging
from pykafka import KafkaClient
import json
import threading
from app.metrics.client import get_metrics_clent
from app.consts import GULDAN_EXC_METRICS_NAME

logger = logging.getLogger(__name__)


class KafkaManager(object):
    def __init__(self, kafka_brokers, kafka_zk, topic_name, broker_version="0.10.0.1"):
        self.kafka_brokers = kafka_brokers
        self.topic_name = topic_name
        self.kafka_client = KafkaClient(
            hosts=self.kafka_brokers, zookeeper_hosts=kafka_zk, broker_version=broker_version,
            socket_timeout_ms=2000, offsets_channel_socket_timeout_ms=2000
        )
        self.kafka_topic = self.kafka_client.topics[self.topic_name]
        self._producer = None

    @property
    def producer(self):
        if not self._producer:
            self._producer = self.kafka_topic.get_producer()

        return self._producer

    def send_message(self, message):
        producer = self.producer
        try:
            producer.produce(message)
        except:
            get_metrics_clent(GULDAN_EXC_METRICS_NAME).write_exc("kafka.send.exc", 1)
            # currently, we ignore the exception here as we can tolerate the message missing
            logger.exception("exc when produce message to kafka")
            try:
                producer.stop()
            except:
                logger.exception("exc when stop producer")
            self._producer = None

    def send_str(self, string):
        self.send_message(string)

    def send_dict(self, dict_message):
        message = json.dumps(dict_message)
        self.send_message(message)


class FakeKafkaManager(object):
    def send_message(self, message):
        pass

    def send_str(self, string):
        pass

    def send_dict(self, dict):
        pass


kafka_manager = None
fake_kafka_manager = FakeKafkaManager()


def try_to_create_kafka_manager(kafka_brokers, kafka_zk, topic_name, broker_version):
    import time
    while True:
        try:
            manager = KafkaManager(kafka_brokers, kafka_zk, topic_name, broker_version)
        except:
            get_metrics_clent(GULDAN_EXC_METRICS_NAME).write_exc("kafka.connect.exc", 1)
            logger.error("trying to connect to kafka, brokers:{}, zk:{}, topic:{}, version:{}".format(
                kafka_brokers, kafka_zk, topic_name, broker_version
            ))
            time.sleep(1)
        else:
            break

    # lock is not used here, as we donot care about the previous one take the fake_kafka_manager
    global kafka_manager
    kafka_manager = manager


def init_kafka_manager(kafka_brokers, kafka_zk, topic_name, broker_version):
    global kafka_manager
    if not kafka_manager:
        try:
            kafka_manager = KafkaManager(kafka_brokers, kafka_zk, topic_name, broker_version)
        except:
            logger.exception("error when init kafka manger, use fake")
            kafka_manager = fake_kafka_manager
            threading.Thread(
                target=try_to_create_kafka_manager, args=(kafka_brokers, kafka_zk, topic_name, broker_version)
            ).start()

    return kafka_manager


def get_kafka_manager():
    return kafka_manager
