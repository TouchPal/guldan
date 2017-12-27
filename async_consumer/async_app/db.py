# -*- coding: utf-8 -*-
import logging
import re
import pymysql
import contextlib

logger = logging.getLogger(__name__)

REGEX = 'mysql://(.*?):(.*?)@(.*?):(.*?)/(.*?)\?(.*)'


def parse_mysql_conn_str(conn_str):
    m = re.match(REGEX, conn_str)
    groups = m.groups()
    if len(groups) < 6:
        raise Exception("invalid mysql conn str: " + conn_str)

    charset_option = groups[5].split("&")[0]

    return {
        "user": groups[0],
        "password": groups[1],
        "host": groups[2],
        "port": int(groups[3]),
        "db": groups[4],
        "charset": charset_option.split("=")[1]
    }


class DBManager(object):
    def __init__(self, address):
        self.address = address
        self.conn_dict = parse_mysql_conn_str(address)
        self.conn_dict["cursorclass"] = pymysql.cursors.DictCursor
        self._db_conn = None

    @property
    def db_conn(self):
        if not self._db_conn:
            self._db_conn = pymysql.Connect(**self.conn_dict)

        return self._db_conn

    @contextlib.contextmanager
    def db_ctx(self):
        db_conn = self.db_conn
        try:
            with db_conn.cursor() as cursor:
                yield cursor
                db_conn.commit()
        except:
            logger.exception("error in db")
            db_conn.rollback()
            db_conn.close()
            self._db_conn = None

    def stop(self):
        if self._db_conn:
            self._db_conn.close()


db_manager = None


def get_db_manager():
    return db_manager


def init_db_manager(db_address):
    global db_manager
    if not db_manager:
        db_manager = DBManager(db_address)

    return db_manager
