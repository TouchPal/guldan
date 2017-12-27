# -*- coding: utf-8 -*-
from sqlalchemy import Column, BigInteger, SmallInteger, String
from flask import g
from app.exc import GulDanException
from .base import Base, Resource


class Privilege(Base):
    __tablename__ = "privilege"

    class Type(object):
        PULLER = 0
        VIEWER = 1
        MODIFIER = 2

        @staticmethod
        def to_str(type_id):
            if type_id == 0:
                return "puller"
            elif type_id == 1:
                return "viewer"
            elif type_id == 2:
                return "modifier"
            else:
                return "unknown_privilege_type"

    resource_id = Column(BigInteger, nullable=False)
    resource_name = Column(String(255), nullable=False)
    resource_type = Column(SmallInteger, nullable=False)
    resource_visibility = Column(SmallInteger, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    user_hash = Column(String(32), nullable=False)
    privilege_type = Column(SmallInteger, nullable=False)

    def __init__(self, res_id, res_name, res_type, user_id, user_hash, pri_type, res_visibility=Resource.Visibility.PRIVATE):
        self.resource_id = res_id
        self.resource_name = res_name
        self.resource_type = res_type
        self.user_id = user_id
        self.user_hash = user_hash
        self.privilege_type = pri_type
        self.resource_visibility = res_visibility

    def to_dict(self):
        return {
            "resource_id": self.resource_id,
            "resource_name": self.resource_name,
            "resource_type": Resource.Type.to_str(self.resource_type),
            "user_id": self.user_id,
            "user_hash": self.user_hash,
            "privilege_type": Privilege.Type.to_str(self.privilege_type)
        }

    @staticmethod
    def add_with_check(res_id, res_name, res_type, user_id, user_hash, pri_type,
                         res_visibility=Resource.Visibility.PRIVATE):
        privilege = g.db_session.query(Privilege).filter_by(
            is_deleted=0,
            resource_id=res_id,
            resource_name=res_name,
            resource_type=res_type,
            user_hash=user_hash,
            privilege_type=pri_type
        ).limit(1).first()
        if privilege:
            return

        g.db_session.add(Privilege(res_id, res_name, res_type, user_id, user_hash, pri_type,
                           res_visibility=res_visibility))

    @staticmethod
    def get_resource_names_under_user(user_hash):
        return g.db_session.query(Privilege.resource_name).filter(
            Privilege.is_deleted == 0,
            Privilege.user_hash == user_hash
        ).all()

    @staticmethod
    def get_privileges_under_user_for_resource(user_hash, resource_type_list, privileges_list):
        return g.db_session.query(Privilege).filter(
            Privilege.is_deleted == 0,
            Privilege.user_hash == user_hash,
            Privilege.resource_type.in_(resource_type_list),
            Privilege.privilege_type.in_(privileges_list)
        ).all()

    @staticmethod
    def get_privilege_by_user_and_resource(user_hash, resource_id, res_type):
        return g.db_session.query(Privilege).filter(
            Privilege.is_deleted == 0,
            Privilege.user_hash == user_hash,
            Privilege.resource_id == resource_id,
            Privilege.resource_type == res_type
        ).limit(1).first()

    @staticmethod
    def get_privileges_under_user(user_hash, resource_type, resource_ids):
        return g.db_session.query(Privilege).filter(
            Privilege.is_deleted == 0,
            Privilege.user_hash == user_hash,
            Privilege.resource_type == resource_type,
            Privilege.resource_id.in_(resource_ids)
        ).all()

    @staticmethod
    def update_privilege_type(res_id, res_type, user_hash, target_privilege_type):
        g.db_session.query(Privilege).filter_by(
            is_deleted=0,
            resource_id=res_id,
            resource_type=res_type,
            user_hash=user_hash
        ).update({Privilege.privilege_type: target_privilege_type})

    @staticmethod
    def get_user_hash_for_resource(res_id, res_type, target_privileges):
        return g.db_session.query(Privilege.user_hash).filter(
            Privilege.is_deleted == 0,
            Privilege.resource_id == res_id,
            Privilege.resource_type == res_type,
            Privilege.privilege_type.in_(target_privileges)
        ).all()

    @staticmethod
    def get_privileges_by_resource(resource_id, resource_type):
        return g.db_session.query(Privilege).filter(
            Privilege.is_deleted == 0,
            Privilege.resource_id == resource_id,
            Privilege.resource_type == resource_type
        ).all()

    @staticmethod
    def get_privilege_by_user_hash_and_resource_name(user_hash, resource_name, resource_type):
        return g.db_session.query(Privilege).filter(
            Privilege.is_deleted == 0,
            Privilege.resource_type == resource_type,
            Privilege.user_hash == user_hash,
            Privilege.resource_name == resource_name
        ).first()

    @staticmethod
    def get_privileges_by_name_prefix(name, user_hash):
        return g.db_session.query(Privilege).filter(
            Privilege.is_deleted == 0,
            Privilege.user_hash == user_hash,
            Privilege.resource_name.like("{}%".format(name)),
        ).all()

    @staticmethod
    def delete_privilege(user_hash, resource_id, resource_type):
        privilege = g.db_session.query(Privilege).filter(
            Privilege.is_deleted == 0,
            Privilege.resource_id == resource_id,
            Privilege.resource_type == resource_type,
            Privilege.user_hash == user_hash
        ).first()
        if not privilege:
            raise GulDanException().with_message(
                u"用户没有改资源的权限，请尝试删除它上级资源的权限"
            ).with_code(404)

        privilege.is_deleted = 1

    @staticmethod
    def delete(resource_id, resource_type):
        g.db_session.query(Privilege).filter(
            Privilege.is_deleted == 0,
            Privilege.resource_id == resource_id,
            Privilege.resource_type == resource_type
        ).update({Privilege.is_deleted: 1})

    @staticmethod
    def get_one_user_for_resource(res_id, res_type, privilege_type):
        return g.db_session.query(Privilege.user_id).filter(
            Privilege.is_deleted == 0,
            Privilege.resource_id == res_id,
            Privilege.resource_type == res_type,
            Privilege.privilege_type == privilege_type
        ).first()
