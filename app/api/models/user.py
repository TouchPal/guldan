# -*- coding: utf-8 -*-
from sqlalchemy import Column, String
from flask import g
from app.exc import GulDanException
from .base import Base


class User(Base):

    __tablename__ = "user"

    name = Column(String(64), nullable=False, unique=True)
    secret_hash = Column(String(32), nullable=False)  # used for login validation
    user_hash = Column(String(32), nullable=False) # used for puller

    def __init__(self, name, secret_hash, user_hash):
        self.name = name
        self.secret_hash = secret_hash
        self.user_hash = user_hash

    def __repr__(self):
        return "<User {}>".format(self.name)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "user_hash": self.user_hash
        }

    @staticmethod
    def add_with_check(user_name, secrect_hash, user_hash):
        user = g.db_session.query(User).filter_by(name=user_name, is_deleted=0).limit(1).first()
        if user:
            raise GulDanException().with_message(u"用户({})已经存在".format(user_name)).with_code(409)

        g.db_session.add(User(user_name, secrect_hash, user_hash))

    @staticmethod
    def get_user_by_name(user_name):
        result = g.db_session.query(User).filter_by(name=user_name, is_deleted=0).first()
        if not result:
            return User("", "", "")

        return result

    @staticmethod
    def get_user_by_user_hash(user_hash):
        return g.db_session.query(User).filter(
                User.user_hash == user_hash,
                User.is_deleted == 0
            ).limit(1).first()

    @staticmethod
    def get_user_hash_by_name(user_name, limit=1):
        result = g.db_session.query(User.user_hash).filter_by(name=user_name, is_deleted=0).limit(limit).first()
        if not result:
            return ""

        return result[0]

    @staticmethod
    def update_user(user_id, name, secret_hash):
        user = g.db_session.query(User).filter_by(id=user_id, is_deleted=0).limit(1).first()
        if not user:
            raise GulDanException().with_message(u"用户(id:{})没有找到".format(user_id)).with_code(404)

        user.name = name
        user.secret_hash = secret_hash

    @staticmethod
    def search_user_by_name(user_name):
        return g.db_session.query(User).filter(User.name.like("%" + user_name + "%")).all()

    @staticmethod
    def delete_by_user_hash(user_hash):
        user = g.db_session.query(User).filter(
            User.is_deleted == 0,
            User.user_hash == user_hash
        ).first()

        if not user:
            raise GulDanException().with_code(404).with_message(u"找不到用户该用户")

        user.is_deleted = 1

        return user
