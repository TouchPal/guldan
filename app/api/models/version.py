# -*- coding: utf-8 -*-
from flask import g
from sqlalchemy import Column, SmallInteger, desc as sql_desc, asc as sql_asc
from sqlalchemy.dialects.mysql import BIGINT, LONGTEXT
from app.api.models.base import Base


class ResourceVersion(Base):

    __tablename__ = "version"

    resource_id = Column(BIGINT(unsigned=True), nullable=False)
    resource_type = Column(SmallInteger, nullable=False)
    version_id = Column(BIGINT(unsigned=True), nullable=False)
    resource_content = Column(LONGTEXT, nullable=False)
    resource_visibility = Column(SmallInteger, nullable=False)
    type = Column(SmallInteger, default=0)

    def __init__(self, resource_id, resource_type, version_id, resource_content, resource_visibility, type=0):
        self.resource_id = resource_id
        self.resource_type = resource_type
        self.version_id = version_id
        self.resource_content = resource_content
        self.resource_visibility = resource_visibility
        self.type = type

    def to_dict(self):
        return {
            "resource_id": self.resource_id,
            "resource_type": self.resource_type,
            "version_id": self.version_id,
            "resource_content": self.resource_content,
            "resource_visibility": self.resource_visibility,
            "type": self.type
        }

    @staticmethod
    def get_all_versions(resource_id, resource_type, limit=10, offset=0, desc=True):
        if desc:
            order_by_func = sql_desc
        else:
            order_by_func = sql_asc

        return g.db_session.query(ResourceVersion).order_by(
            order_by_func(ResourceVersion.version_id)
        ).filter(
            ResourceVersion.is_deleted == 0,
            ResourceVersion.resource_id == resource_id,
            ResourceVersion.resource_type == resource_type
        ).limit(limit).offset(offset).all()

    @staticmethod
    def get_versions_count(resource_id, resource_type):
        return g.db_session.query(ResourceVersion).filter(
            ResourceVersion.is_deleted == 0,
            ResourceVersion.resource_id == resource_id,
            ResourceVersion.resource_type == resource_type
        ).count()

    @staticmethod
    def get_versions_by_resource(resource_id, resource_type, version_ids):
        return g.db_session.query(ResourceVersion).filter(
            ResourceVersion.is_deleted == 0,
            ResourceVersion.resource_id == resource_id,
            ResourceVersion.resource_type == resource_type,
            ResourceVersion.version_id.in_(version_ids)
        ).all()

    @staticmethod
    def get_by_version(resource_id, resource_type, version_id):
        return g.db_session.query(ResourceVersion).filter(
            ResourceVersion.is_deleted == 0,
            ResourceVersion.resource_id == resource_id,
            ResourceVersion.resource_type == resource_type,
            ResourceVersion.version_id == version_id
        ).first()
