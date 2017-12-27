# -*- coding: utf-8 -*-
import logging
from pykafka import KafkaClient
import json
import threading
from async_app.consts import GULDAN_EXC_METRICS_NAME
from async_app.metrics.client import get_metrics_clent

logger = logging.getLogger(__name__)


def convert_version_str_to_int(version_str):
    final = 0
    version_splits = version_str.split(".")
    for s in range(3):
        final = final * 10 + int(version_splits[s])

    return final


class KafkaManager(object):
    VERSION_INT_FOR_0_9 = 90

    def __init__(self, kafka_brokers, kafka_zk, topic_name, consumer_group_name, broker_version="0.10.0.1"):
        self.kafka_brokers = kafka_brokers
        self.kafka_zk = kafka_zk
        self.kafka_client = KafkaClient(hosts=self.kafka_brokers, zookeeper_hosts=kafka_zk, broker_version=broker_version)
        self.topic_name = topic_name
        self.consumer_group_name = consumer_group_name
        self.kafka_topic = self.kafka_client.topics[self.topic_name]
        self.version_int = convert_version_str_to_int(broker_version)
        self.can_be_managed = True if self.version_int >= KafkaManager.VERSION_INT_FOR_0_9 else False
        self._consumer = None
        self._producer = None

    @property
    def consumer(self):
        if not self._consumer:
            self._consumer = self.kafka_topic.get_balanced_consumer(
                self.consumer_group_name, managed=False,
                auto_commit_enable=True
            )

        return self._consumer

    def consume(self):
        consumer = self.consumer
        try:
            return consumer.consume()
        except:
            get_metrics_clent(GULDAN_EXC_METRICS_NAME).write_exc("kafka.consume.exc", 1)
            logger.exception("exc when consuming message from kafka")
            try:
                consumer.stop()
            except:
                logger.exception("exc when stop consumer")
            self._consumer = None

    def consume_dict(self):
        message = self.consume()
        dict_str = message.value
        return json.loads(dict_str)

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

    def stop(self):
        if self._consumer:
            self._consumer.commit_offsets()
            self._consumer.stop()


class FakeKafkaManager(object):
    def consume_dict(self):
        return {}

    def send_message(self, message):
        pass

    def send_str(self, string):
        pass

    def send_dict(self, dict):
        pass

    def stop(self):
        pass


kafka_manager = None
fake_kafka_manager = FakeKafkaManager()


def try_to_create_kafka_manager(kafka_brokers, kafka_zk, topic_name, consumer_group_name, broker_version):
    import time
    while True:
        try:
            manager = KafkaManager(kafka_brokers, kafka_zk, topic_name, consumer_group_name, broker_version=broker_version)
        except:
            get_metrics_clent(GULDAN_EXC_METRICS_NAME).write_exc("kafka.connect.exc", 1)
            logger.error("trying to connect to kafka, brokers:{}, zk:{}, topic:{}, version:{}, consumer_group:{}".format(
                kafka_brokers, kafka_zk, topic_name, broker_version, consumer_group_name
            ))
            time.sleep(1)
        else:
            break

    # lock is not used here, as we donot care about the previous one take the fake_kafka_manager
    global kafka_manager
    kafka_manager = manager


def get_kafka_manager():
    return kafka_manager


def init_kafka_manager(configs):
    global kafka_manager
    if not kafka_manager:
        try:
            kafka_manager = KafkaManager(
                configs["kafka_brokers"], configs["kafka_zk"], configs["kafka_item_grey_topic"],
                configs["kafka_consumer_group_name"], broker_version=configs["kafka_version"]
            )
        except:
            logger.exception("error to connect to kafka")
            kafka_manager = fake_kafka_manager
            threading.Thread(target=try_to_create_kafka_manager, args=(
                configs["kafka_brokers"], configs["kafka_zk"], configs["kafka_item_grey_topic"],
                configs["kafka_consumer_group_name"], configs["kafka_version"]
            )).start()


    return kafka_manager
