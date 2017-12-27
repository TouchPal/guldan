# -*- coding: utf-8 -*-
from flask import g
from app.exc import GulDanException
from .base import Resource


class Org(Resource):

    __tablename__ = "org"

    def __init__(self, name, visibility=Resource.Visibility.PRIVATE):
        self.name = name
        self.visibility = visibility

    def __repr__(self):
        return "<Org {}>".format(self.name)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "visibility": Resource.Visibility.to_str(self.visibility)
        }

    @staticmethod
    def update_org(org_id, org_name):
        org = g.db_session.query(Org).filter_by(id=org_id, is_deleted=0).limit(1).first()
        if not org:
            raise GulDanException().with_message(u"没有找到组织(id:{})".format(org_id)).with_code(404)

        org.name = org_name


