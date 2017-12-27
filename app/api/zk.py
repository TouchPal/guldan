# -*- coding: utf-8 -*-
import atexit
import contextlib
import logging
import time
from collections import deque

from kazoo.client import KazooClient

from app import load_app_config
from app.exc import GulDanException

logger = logging.getLogger(__name__)

class Session(object):
    def __init__(self, conn, timeout):
        self.conn = conn
        self.timeout = timeout
        self.created_at = time.time()

    def should_close(self):
        if not self.conn.connected:
            return True

        return self.created_at + self.timeout < time.time()

    def start(self):
        self.conn.start()

    def close(self):
        self.conn.stop()
        self.conn.close()


class ZKManager(object):
    def __init__(self, zk_config, initial_conns=3, max_conns=10, session_timeout=300):
        self.zksessions = deque()
        self.zk_config = zk_config
        self.initial_conns = initial_conns
        self.max_conns = max_conns
        self.session_timeout = session_timeout

    def create_zk_sessions(self):
        for i in range(self.initial_conns):
            self.add_session(self.zk_config)

    def add_session(self, zk_config):
        if len(self.zksessions) > self.max_conns:
            return

        conn = KazooClient(**zk_config)
        session = Session(conn, self.session_timeout)
        self.zksessions.append(session)
        session.start()

    def _acquire_session(self):
        session = None
        while self.zksessions:
            session = self.zksessions.pop()
            if session.should_close():
                session.close()
                self.add_session(self.zk_config)
                logger.warning("zk conn time out ,create a new one")
                session = None
            else:
                break

        return session

    def return_session(self, session):
        self.zksessions.append(session)

    @contextlib.contextmanager
    def zk_session_ctx(self):
        session = None
        try:
            session = self._acquire_session()
            if not session:
                raise GulDanException().with_code(500).with_message(u"不能连接到zookeeper")

            yield session
        finally:
            self.return_session(session)

    def is_path_existing(self, path):
        with self.zk_session_ctx() as session:
            if session.conn.exists(path):
                return True

        return False

    def close_sessions(self):
        for s in self.zksessions:
            s.close()

app_config = load_app_config()

zk_manager = ZKManager(
    app_config.ZK_CONN_CONFIG,
    **app_config.ZK_MANAGER_CONFIG
)

atexit.register(zk_manager.close_sessions)

