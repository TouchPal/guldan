# -*- coding: utf-8 -*-
import contextlib
import logging
import random

from flask import request, g
from sqlalchemy import create_engine as sqlalchemy_create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from app import app, load_app_config
from app.exc import GulDanException
from stats import sys_stats

logger = logging.getLogger(__name__)

def model_base():
    return declarative_base()


class RecycleField(object):
    def __get__(self, instance, klass):
        if instance is not None:
            return int(random.uniform(0.75, 1) * instance._origin_recyle)
        raise AttributeError


def patch_engine(engine):
    pool = engine.pool
    pool._origin_recyle = pool._recycle
    del pool._recycle
    setattr(pool.__class__, '_recycle', RecycleField())
    return engine


def maintainance_check(session, flush_context, instances):
    raise GulDanException().with_code(500).with_message(u"guldan维护中，禁止写入")


class DBManager(object):

    def __init__(self, stats):
        self.session_map = {}
        self.create_sessions()
        self.stats = stats

    def create_sessions(self):
        db_settings = load_app_config().DB_SETTINGS
        for role, url in db_settings.items():
            session_factory = self.create_single_session(url)
            # event.listen(session_factory, "before_flush", maintainance_check)
            self.session_map[role] = session_factory

    @classmethod
    def create_single_session(cls, url, scopefunc=None):
        engine = sqlalchemy_create_engine(url,
            pool_size=10,
            max_overflow=70,
            pool_recycle=1200
        )
        patched_engine = patch_engine(engine)
        return scoped_session(
            sessionmaker(
                expire_on_commit=False,
                bind=patched_engine
            ),
            scopefunc=scopefunc
        )

    def get_session(self, name):
        try:
            if not name:
                name = "master"

            return self.session_map[name]
        except KeyError:
            raise KeyError('{} not created, check your DB_SETTINGS'.format(name))
        except IndexError:
            raise IndexError('cannot get names from DB_SETTINGS')

    @contextlib.contextmanager
    def session_ctx(self, bind=None):
        DBSession = self.get_session(bind)
        session = DBSession()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.expunge_all()
            session.close()
            DBSession.remove()

db_manager = DBManager(sys_stats)




