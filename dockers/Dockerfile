FROM ubuntu:14.04

ADD requirements.txt /tmp
RUN apt-get update && apt-get install -y python-pip libmysqlclient-dev python2.7-dev curl \
    && pip install pip --upgrade
RUN pip install -r /tmp/requirements.txt

VOLUME ["/logs", "/crash", "/ssd"]
