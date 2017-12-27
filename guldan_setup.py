# -*- coding: utf-8 -*-
#!/usr/bin/env python
import functools
import click
import subprocess
import MySQLdb
import time
import yaml
import re
from urlparse import urlparse
from jinja2 import Template

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
DOCKER_COMPOSE_PROJECT_NAME = "guldan_dependencies"
GULDAN_WEB_CONTAINER_NAME = "guldan_web"
GULDAN_ASYNC_CONTAINER_NAME = "guldan_async"
GULDAN_BASE_DOCKERFILE = "./dockers/Dockerfile"
GULDAN_WEB_DOCKERFILE = "./Dockerfile"
GULDAN_ASYNC_CONSUMER_DOCKERFILE = "./async_consumer/Dockerfile"
GULDAN_DEPENDENCY_SETUP_COMPOSE_FILE = "./docker-compose/docker-compose-for-setup.yml"


def wait_for_mysql(server, port):
    while True:
        try:
            db_conn = MySQLdb.connect(host=server, port=port, user="root", password="root")
            with db_conn.cursor() as cursor:
                cursor.execute("select 1")
        except:
            print "wait for mysql to come up"
            time.sleep(1)
        else:
            break


def _read(fpath):
    with open(fpath, 'rb') as f:
        return f.read()


def _write(fpath, content):
    with open(fpath, 'wb') as f:
        f.write(content)


def generate_conf_from_template(fpath, new_path, **kwargs):
    content = Template(_read(fpath)).render(**kwargs)

    _write(new_path, content)


@click.group(context_settings=CONTEXT_SETTINGS)
def entry_point():
    pass


def print_func_name(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print "------{}------".format(func.__name__)
        return func(*args, **kwargs)

    return wrapper


@print_func_name
def start_guldan_dependencies(configs):
    generate_conf_from_template(
        "./docker-compose/docker-compose-for-setup.yml.jinja",
        "./docker-compose/docker-compose-for-setup.yml",
        **configs
    )
    subprocess.call(["docker-compose", "-f", GULDAN_DEPENDENCY_SETUP_COMPOSE_FILE, "-p", DOCKER_COMPOSE_PROJECT_NAME, "up", "-d"])


BLANKS_IN_SQL_COMMAND = [" ", "\n", "\t"]

def is_empty_sql_command(command):
    for s in command:
        if s in BLANKS_IN_SQL_COMMAND:
            continue
        return False

    return True

@print_func_name
def prepare_db(configs):
    mysql_port = int(configs["mysql_port"])
    wait_for_mysql("127.0.0.1", mysql_port)
    with open("./app/api/models/models.sql") as f:
        sql_script = f.read()

    sql_commands = sql_script.split(";")
    db_conn = MySQLdb.connect(host="127.0.0.1", port=mysql_port, user="root", password="root")
    try:
        with db_conn.cursor() as cursor:
            for command in sql_commands:
                if not is_empty_sql_command(command):
                    cursor.execute(command)
        db_conn.commit()
    finally:
        db_conn.close()


@print_func_name
def build_guldan_base():
    subprocess.call(["docker", "build", "-f", GULDAN_BASE_DOCKERFILE, "-t", "guldan_base:latest", "./dockers"])


@print_func_name
def build_guldan_web():
    subprocess.call(["docker", "build", "-f", GULDAN_WEB_DOCKERFILE, "-t", "guldan:latest", "."])


def generate_guldan_web_env(configs):
    envs = ["-e", "GULDAN_CONFIG_TYPE=env"]
    for k, v in configs.items():
        envs.append("-e")
        envs.append("{}={}".format(k, v))

    return envs


def generate_guldan_web_docker_command(container_name, external_port, internal_port, envs):
    return "docker run -d --sysctl net.core.somaxconn=65535 --name={} -v /etc/localtime:/etc/localtime -p {}:{} {} guldan:latest".format(
        container_name, external_port, internal_port, " ".join(envs)
    )


@print_func_name
def start_guldan_web(port=None, configs=None):
    envs = generate_guldan_web_env(configs)
    command = generate_guldan_web_docker_command(GULDAN_WEB_CONTAINER_NAME, port, configs["port"], envs)

    subprocess.call(re.split("\s+", command))


@print_func_name
def build_guldan_async():
    subprocess.call(["docker", "build", "-f", GULDAN_ASYNC_CONSUMER_DOCKERFILE, "-t", "guldan_async:latest","./async_consumer"])


def generate_guldan_async_envs(guldan_async_configs):
    envs = ["-e", "GULDAN_CONFIG_TYPE=env"]
    for k, v in guldan_async_configs.items():
        envs.append("-e")
        envs.append("{}={}".format(k, v))

    return envs


def generate_guldan_async_docker_command(container_name, envs):
    return "docker run -d --name={} -v /etc/localtime:/etc/localtime {} guldan_async:latest".format(
        container_name, " ".join(envs)
    )


@print_func_name
def start_guldan_async(configs=None):
    envs = generate_guldan_async_envs(configs)
    command = generate_guldan_async_docker_command(GULDAN_ASYNC_CONTAINER_NAME, envs)
    subprocess.call(re.split("\s+", command))


def get_guldan_configs(guldan_option_file):
    with open(guldan_option_file, "r") as f:
        guldan_configs = yaml.load(f)

    guldan_configs["kafka_broker_port"] = guldan_configs["kafka_brokers"].split(":")[1]
    guldan_configs["kafka_zk_port"] = guldan_configs["kafka_zk"].split(":")[1]
    guldan_configs["redis_port"] = guldan_configs["redis_url"].split(":")[2].split("/")[0]

    mysql_url = urlparse(guldan_configs["db_master"])
    guldan_configs["mysql_port"] = mysql_url.port

    return guldan_configs


@click.command(help="build docker images and bring them up")
@click.option("--guldan-port", type=int, help="the host port that will be mapped to guldan", required=True)
@click.option("--guldan-option-file", type=str, help="the location of the config file for guldan", required=True)
def run(guldan_port, guldan_option_file):
    guldan_configs = get_guldan_configs(guldan_option_file)

    start_guldan_dependencies(guldan_configs)
    prepare_db(guldan_configs)
    build_guldan_base()
    build_guldan_web()
    start_guldan_web(port=guldan_port, configs=guldan_configs)
    build_guldan_async()
    start_guldan_async(configs=guldan_configs)


@print_func_name
def stop_guldan_async():
    subprocess.call(["docker", "stop", GULDAN_ASYNC_CONTAINER_NAME])


@print_func_name
def rm_guldan_async():
    subprocess.call(["docker", "rm", GULDAN_ASYNC_CONTAINER_NAME])


@print_func_name
def stop_gudlan_web():
    subprocess.call(["docker", "stop", GULDAN_WEB_CONTAINER_NAME])


@print_func_name
def rm_guldan_web():
    subprocess.call(["docker", "rm", GULDAN_WEB_CONTAINER_NAME])


@print_func_name
def guldan_dependencies_down():
    subprocess.call(["docker-compose", "-f", GULDAN_DEPENDENCY_SETUP_COMPOSE_FILE ,"-p", DOCKER_COMPOSE_PROJECT_NAME, "down"])


@click.command(help="bring down and remove containers")
def down():
    stop_guldan_async()
    rm_guldan_async()
    stop_gudlan_web()
    rm_guldan_web()
    guldan_dependencies_down()


@click.group(help="reload only one container")
def reload():
    pass


def rmi_guldan_web():
    subprocess.call(["docker", "rmi", "guldan:latest"])


@click.command(help="reload guldan web", name="guldan")
@click.option("--guldan-port", type=int, help="the host port that will be mapped to guldan", required=True)
@click.option("--guldan-option-file", type=str, help="the location of the config file for guldan", required=True)
def reload_guldan_web(guldan_port, guldan_option_file):
    guldan_configs = get_guldan_configs(guldan_option_file)
    stop_gudlan_web()
    rm_guldan_web()
    rmi_guldan_web()
    build_guldan_web()
    start_guldan_web(guldan_port, guldan_configs)


def rmi_guldan_async():
    subprocess.call(["docker", "rmi", "guldan_async:latest"])


@click.command(help="reload guldan async", name="guldan_async")
@click.option("--guldan-option-file", type=str, help="the location of the config file for guldan", required=True)
def reload_guldan_async(guldan_option_file):
    guldan_configs = get_guldan_configs(guldan_option_file)
    stop_guldan_async()
    rm_guldan_async()
    rmi_guldan_async()
    build_guldan_async()
    start_guldan_async(configs=guldan_configs)


if __name__ == "__main__":
    reload.add_command(reload_guldan_web)
    reload.add_command(reload_guldan_async)

    entry_point.add_command(run)
    entry_point.add_command(down)
    entry_point.add_command(reload)
    entry_point()
