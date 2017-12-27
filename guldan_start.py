# -*- coding: utf-8 -*-
import os
import subprocess
import socket
from jinja2 import Template

CURRRENT_DIR = os.getcwd()
JINJAS_DIR = os.path.join(CURRRENT_DIR, "jinjas")
HOSTNAME = socket.getfqdn()
GULDAN_ENV_CONFIG_LIST = [
    "db_master",
    "db_slave",
    "protocol",
    "port",
    "redis_url",
    "metrics_url",
    "kafka_zk",
    "kafka_brokers",
    "kafka_item_grey_topic",
    "kafka_version",
    "salt",
]


def _read(fpath):
    with open(fpath, 'rb') as f:
        return f.read()


def _write(fpath, content):
    with open(fpath, 'wb') as f:
        f.write(content)


def generate_conf_from_template(fpath, new_path, **kwargs):
    content = Template(_read(fpath)).render(**kwargs)

    _write(new_path, content)


def generate_conf_from_dict(config_dict):
    generate_conf_from_template(
        os.path.join(JINJAS_DIR, "guldan_configs.yml.jinja"),
        os.path.join(CURRRENT_DIR, "guldan_configs.yml"),
        **config_dict
    )
    generate_conf_from_template(
        os.path.join(JINJAS_DIR, "guldan_uwsgi.ini.jinja"),
        os.path.join(CURRRENT_DIR, "guldan_uwsgi.ini"),
        **config_dict
    )


def run_guldan():
    subprocess.call("mkdir -p /logs/guldan", shell=True)
    os.execlp("uwsgi", "uwsgi", "/webapp/guldan_uwsgi.ini")


def generate_config_files():
    configs = {}
    for config_name in GULDAN_ENV_CONFIG_LIST:
        configs[config_name] = os.getenv(config_name)

    generate_conf_from_dict(configs)


if __name__ == "__main__":
    generate_config_files()
    run_guldan()
