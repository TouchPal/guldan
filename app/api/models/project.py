# -*- coding: utf-8 -*-
from sqlalchemy import Column, BigInteger
from flask import g
from .base import Resource, ChildResourceMixin


class Project(ChildResourceMixin, Resource):

    __tablename__ = "project"

    parent_id = Column(BigInteger, nullable=False)

    def __init__(self, name, org_id, visibility=Resource.Visibility.PRIVATE):
        self.name = name
        self.parent_id = org_id
        self.visibility = visibility

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "parent_id": self.parent_id,
            "visibility": Resource.Visibility.to_str(self.visibility)
        }

    @staticmethod
    def get_projects_under_org(org_id):
        return g.db_session.query(Project).filter_by(
            is_deleted=0,
            parent_id=org_id
        ).all()
