# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import yaml

app_base_dir = os.path.abspath(os.path.dirname(__file__))


class FlaskConfig(object):
    # Statement for enabling the development environment
    DEBUG = False
    SQLALCHEMY_ECHO=False
    JSON_AS_ASCII=False

    # Define the application directory
    BASE_DIR = app_base_dir

    SEND_FILE_MAX_AGE_DEFAULT = 0
    TEMPLATES_AUTO_RELOAD = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True


class AppConfig(object):
    APP_NAME = "guldan"
    LOG_PATH_PREFIX = "/logs/guldan"
    LISTENING_PORT = 5000

    DB_SETTINGS = {
        'master': 'mysql://root:root@127.0.0.1:3500/guldandb?charset=utf8mb4',
        'slave': 'mysql://root:root@127.0.0.1:3500/guldandb?charset=utf8mb4'
    }

    SALT_STRING = "test"
    REDIS_URL = "redis://127.0.0.1:16379/6"
    METRICS_URL = "unset"
    KAFKA_BROKERS = "127.0.0.1:10002"
    KAFKA_ZK = "127.0.0.1:2182"
    KAFKA_ITEM_GREY_TOPIC = "guldan_item_grey"
    KAFKA_VERSION = "0.10.0.1"

    def _load_configs_from_file(self):
        try:
            with open(os.path.join(app_base_dir, 'guldan_configs.yml')) as f:
                configs = yaml.load(f)
                AppConfig.DB_SETTINGS['master'] = configs['db_master']
                AppConfig.DB_SETTINGS['slave'] = configs['db_slave']
                AppConfig.SALT_STRING = configs['salt']
                AppConfig.METRICS_URL = configs['metrics_url']
                AppConfig.REDIS_URL = configs['redis_url']
                AppConfig.KAFKA_BROKERS = configs['kafka_brokers']
                AppConfig.KAFKA_ZK = configs['kafka_zk']
                AppConfig.KAFKA_ITEM_GREY_TOPIC = configs['kafka_item_grey_topic']
                AppConfig.KAFKA_VERSION = configs['kafka_version']
                return True
        except:
            return False

    def refresh_configs(self):
        if self._load_configs_from_file():
            print("successfully get configs from conf server")
        else:
            print("cannot get configs from env, use default")