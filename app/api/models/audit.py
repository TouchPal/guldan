# -*- coding: utf-8 -*-
from flask import g
from sqlalchemy import Column, SmallInteger, desc
from sqlalchemy.dialects.mysql import BIGINT
from .base import Base


class Audit(Base):
    __tablename__ = "audit"

    user_id = Column(BIGINT(unsigned=True), nullable=False)
    action = Column(SmallInteger, nullable=False)
    resource_id = Column(BIGINT(unsigned=True), nullable=False)
    resource_type = Column(SmallInteger, nullable=False)
    version_id = Column(BIGINT(unsigned=True), default=1)

    class Action(object):
        CREATE = 0
        MODIFY = 1
        DELETE = 2

        @staticmethod
        def to_str(action_type):
            if action_type == Audit.Action.CREATE:
                return "create"
            elif action_type == Audit.Action.MODIFY:
                return "modify"
            elif action_type == Audit.Action.DELETE:
                return "delete"
            else:
                return "unknown action type"

    def __init__(self, user_id, action, resource_id, resource_type, version_id):
        self.user_id = user_id
        self.action = action
        self.resource_id = resource_id
        self.resource_type = resource_type
        self.version_id = version_id

    @staticmethod
    def get_audit_for_resource_id(resource_id, resource_type, offset=0, limit=100):
        return g.db_session.query(Audit).order_by(desc(Audit.created_at)).filter(
            Audit.is_deleted == 0,
            Audit.resource_id == resource_id,
            Audit.resource_type == resource_type
        ).offset(offset).limit(limit).all()

    @staticmethod
    def get_audit_count_for_resource(resource_id, resource_type):
        return g.db_session.query(Audit).filter(
            Audit.is_deleted == 0,
            Audit.resource_id == resource_id,
            Audit.resource_type == resource_type
        ).count()

