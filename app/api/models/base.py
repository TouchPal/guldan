# -*- coding: utf-8 -*-
from sqlalchemy import Column, BigInteger, SmallInteger, DateTime, String
from sqlalchemy.dialects.mysql import BIGINT
from flask import g
from app.db import model_base

DeclarativeBase = model_base()

import datetime
from app.exc import GulDanException
from app.api.utils.helper import valid_int

import logging
logger = logging.getLogger(__name__)


class Base(DeclarativeBase):

    __abstract__ = True

    id = Column(BigInteger, primary_key=True)
    is_deleted = Column(SmallInteger, default=0)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    created_at = Column(DateTime, default=datetime.datetime.now)

    @classmethod
    def add(cls, res):
        g.db_session.add(res)
        # let us refresh to get the primary_key from db
        g.db_session.flush()
        g.db_session.refresh(res)

    @classmethod
    def get_all(cls, offset=0, limit=10):
        return g.db_session.query(cls).filter_by(is_deleted=0).limit(limit).offset(offset).all()

    @classmethod
    def get_by_id(cls, object_id):
        return g.db_session.query(cls).filter_by(id=object_id, is_deleted=0).first()

    @classmethod
    def get_by_id_for_audit(cls, object_id):
        return g.db_session.query(cls).filter_by(id=object_id).first()

    @classmethod
    def get_by_ids(cls, object_ids):
        if not object_ids:
            return []

        return g.db_session.query(cls).filter(cls.is_deleted==0, cls.id.in_(object_ids)).all()

    @classmethod
    def delete_by_id(cls, object_id):
        object = g.db_session.query(cls).filter_by(id=object_id, is_deleted=0).limit(1).first()
        if not object:
            raise GulDanException().with_message(u"{} id:{} 找不到".format(
                cls.__name__, object_id)
            ).with_code(404)

        object.is_deleted = 1


class Resource(Base):

    __abstract__ = True

    class Type(object):
        ORG = 1
        PROJECT = 2
        ITEM = 3

        @staticmethod
        def to_str(type_id):
            if type_id == 1:
                return "org"
            elif type_id == 2:
                return "project"
            elif type_id == 3:
                return "item"
            else:
                return "unknown_resource_type"

        @staticmethod
        def parse_from_int(type_id):
            if type_id == 1:
                return Resource.Type.ORG
            elif type_id == 2:
                return Resource.Type.PROJECT
            elif type_id == 3:
                return Resource.Type.ITEM
            else:
                raise GulDanException().with_code(400).with_message(u"非法的资源类型: " + type_id)

    class Visibility(object):
        PRIVATE = 0
        PUBLIC = 1

        @staticmethod
        def to_str(v_id):
            if v_id == 0:
                return "private"
            elif v_id == 1:
                return "public"
            else:
                return "unknown_visibility_type"

        @staticmethod
        def is_valid(visibility):
            if visibility is None:
                return False
            
            try:
                v = valid_int(visibility)
            except ValueError:
                return False

            if v in (Resource.Visibility.PUBLIC, Resource.Visibility.PRIVATE):
                return True

            return False

        @staticmethod
        def convert(visibility):
            return int(visibility)

    name = Column(String(255), nullable=False)
    visibility = Column(SmallInteger, nullable=False, default=Visibility.PRIVATE)
    current_version_id = Column(BIGINT(unsigned=True), default=1)

    @classmethod
    def get_by_name(cls, resource_name):
        return g.db_session.query(cls).filter_by(name=resource_name, is_deleted=0).first()

    @classmethod
    def get_by_names(cls, resource_names):
        if not resource_names:
            return []

        return g.db_session.query(cls).filter(cls.name.in_(resource_names), cls.is_deleted==0).all()

    @classmethod
    def get_name_by_id(cls, res_id):
        resource = g.db_session.query(cls.name).filter_by(
            is_deleted=0,
            id=res_id
        ).limit(1).first()
        if not resource:
            raise GulDanException().with_code(404).with_message(
                u"找不到资源, id:{}".format(res_id)
            )

        return resource[0]

    @classmethod
    def set_name(cls, name):
        name_parts = cls.name.split(".")
        name_parts[-1] = name
        cls.name = ".".join(name_parts)

    @classmethod
    def update_visibility(cls, resource_id, visibility):
        return g.db_session.query(cls).filter(
            cls.is_deleted == 0,
            cls.id == resource_id
        ).update({cls.visibility: visibility}, synchronize_session='fetch')


class ChildResourceMixin(object):
    @classmethod
    def delete_by_parent_id(cls, parent_id):
        g.db_session.query(cls).filter_by(is_deleted=0, parent_id=parent_id).update({cls.is_deleted: 1})

    @classmethod
    def get_parent_id(cls, res_id):
        res = cls.get_by_id(res_id)
        if not res:
            raise GulDanException().with_message(u"{}找不到资源, id:{}".format(
                cls.__name__, res_id
            )).with_code(404)

        return res.parent_id

    @classmethod
    def get_by_parent_and_name(cls, parent_id, name):
        return g.db_session.query(cls).filter(
            cls.is_deleted == 0,
            cls.parent_id == parent_id,
            cls.name == name
        ).first()

    @classmethod
    def get_resources_under_parent_id(cls, parent_id):
        return g.db_session.query(cls).filter(
            cls.is_deleted == 0,
            cls.parent_id == parent_id
        ).all()
