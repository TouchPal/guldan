# -*- coding: utf-8 -*-
from sqlalchemy import Column, BigInteger, String
from flask import g
from app.exc import GulDanException
from .base import Base


class UserLogin(Base):

    __tablename__ = "user_login"

    DEFAULT_SESSION_ID = "0"

    user_id = Column(BigInteger, nullable=False, unique=True)
    login_token = Column(String(64), nullable=False, default=DEFAULT_SESSION_ID)

    def __init__(self, user_id, login_token):
        self.user_id = user_id
        self.login_token = login_token

    def __repr__(self):
        return "<UserLogin user_id:{} login_token:{}>".format(
            self.user_id,
            self.login_token
        )

    @staticmethod
    def get_user_login_by_user_id(user_id):
        result = g.db_session.query(UserLogin).filter_by(
            user_id=user_id, is_deleted=0
        ).first()
        if not result:
            return UserLogin("", "")

        return result

    @staticmethod
    def logout_user_by_user_id(user_id, session_id):
        user_login = g.db_session.query(UserLogin).filter_by(
            user_id=user_id, is_deleted=0
        ).limit(1).first()
        if not user_login:
            raise GulDanException().with_message(u"找不到登录信息, user_id:{}".format(
                user_id
            )).with_code(404)

        if user_login.login_token == session_id:
            user_login.login_token = UserLogin.DEFAULT_SESSION_ID
        elif user_login.login_token == UserLogin.DEFAULT_SESSION_ID:
            raise GulDanException().with_message(u"用户(id:{})已经登出".format(user_id)).with_code(409)
        else:
            raise GulDanException().with_message(u"登录信息不匹配，不能登出").with_code(409)

    @staticmethod
    def login_user_by_user_id(user_id, login_token):
        user_login = g.db_session.query(UserLogin).filter_by(
            user_id=user_id, is_deleted=0
        ).limit(1).first()
        if not user_login:
            g.db_session.add(UserLogin(user_id, login_token))
            return

        if user_login.login_token != UserLogin.DEFAULT_SESSION_ID:
            return user_login.login_token

        user_login.login_token = login_token
