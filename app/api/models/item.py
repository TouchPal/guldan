# -*- coding: utf-8 -*-
from sqlalchemy import Column, BigInteger, SmallInteger, String
from sqlalchemy.dialects.mysql import BIGINT, LONGTEXT
from flask import g
from .base import Base, Resource, ChildResourceMixin


class Item(ChildResourceMixin, Resource):

    __tablename__ = "item"

    parent_id = Column(BigInteger, nullable=False)
    data = Column(LONGTEXT, nullable=False)
    type = Column(SmallInteger, nullable=False)
    in_grey = Column(SmallInteger, nullable=False)

    class Type(object):
        INVALID = -1
        PLAIN = 0
        JSON = 1
        XML = 2
        YAML = 3

        @staticmethod
        def to_str(type_id):
            if type_id == Item.Type.PLAIN:
                return "PLAIN"
            elif type_id == Item.Type.JSON:
                return "JSON"
            elif type_id == Item.Type.XML:
                return "XML"
            elif type_id == Item.Type.YAML:
                return "YAML"
            else:
                return "unknown"

        @staticmethod
        def to_type(type_str):
            upper_type_str = type_str.upper()
            if upper_type_str == "PLAIN":
                return Item.Type.PLAIN
            elif upper_type_str == "JSON":
                return Item.Type.JSON
            elif upper_type_str == "XML":
                return Item.Type.XML
            elif upper_type_str == "YAML":
                return Item.Type.YAML
            else:
                return Item.Type.INVALID

    def __init__(self, name, project_id, config_data, type, visibility=Resource.Visibility.PRIVATE, is_grey=False, version_id=None):
        self.name = name
        self.parent_id = project_id
        self.data = config_data
        self.type = type
        self.visibility = visibility
        self.in_grey = 0 if not is_grey else 1
        self.current_version_id = version_id

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "parent_id": self.parent_id,
            "content": self.data,
            "type": Item.Type.to_str(self.type),
            "visibility": Resource.Visibility.to_str(self.visibility)
        }

    @staticmethod
    def get_items_under_project(project_id):
        return g.db_session.query(Item).filter_by(is_deleted=0, parent_id=project_id).all()

    @staticmethod
    def get_public_items_under_project(project_id):
        return g.db_session.query(Item).filter_by(
            is_deleted=0, parent_id=project_id, visibility=Resource.Visibility.PUBLIC
        ).all()

    @staticmethod
    def get_item_under_project(project_id, item_name):
        return g.db_session.query(Item).filter_by(is_deleted=0, parent_id=project_id, name=item_name).first()

    @staticmethod
    def update_with_updated_time(item_id, item_data, item_type, visibility, in_grey, updated_at=None, version_id=None):
        return g.db_session.query(Item).filter(
            Item.is_deleted == 0,
            Item.id == item_id,
            Item.updated_at == updated_at
        ).update({
            Item.data: item_data,
            Item.visibility: visibility,
            Item.in_grey: in_grey,
            Item.type: item_type,
            Item.current_version_id: version_id,
        }, 
        synchronize_session='fetch')

    @staticmethod
    def delete(item_id):
        g.db_session.query(Item).filter(
            Item.is_deleted == 0,
            Item.id == item_id,
        ).update({Item.is_deleted: 1})

    @staticmethod
    def unset_grey(item_id):
        g.db_session.query(Item).filter(
            Item.is_deleted == 0,
            Item.id == item_id
        ).update({Item.in_grey: 0})


class GreyItem(Base):
    __tablename__ = "grey_item"

    item_id = Column(BIGINT(unsigned=True), nullable=False)
    item_name = Column(String(255), nullable=False)
    item_data = Column(LONGTEXT, nullable=False)
    item_type = Column(SmallInteger, nullable=False)
    item_visibility = Column(SmallInteger, nullable=False)
    current_version_id = Column(BIGINT(unsigned=True), default=1)

    def __init__(self, item_id, item_name, item_data, item_type, item_visibility, version_id=None):
        self.item_id = item_id
        self.item_name = item_name
        self.item_data = item_data
        self.item_type = item_type
        self.item_visibility = item_visibility
        self.current_version_id = version_id

    def to_dict(self):
        return {
            "id": self.item_id,
            "name": self.item_name,
            "content": self.item_data,
            "type": Item.Type.to_str(self.item_type),
            "visibility": Resource.Visibility.to_str(self.item_visibility),
            "version_id": self.current_version_id
        }

    @staticmethod
    def get_by_item_id(item_id):
        return g.db_session.query(GreyItem).filter(
            GreyItem.is_deleted == 0,
            GreyItem.item_id == item_id
        ).first()

    @staticmethod
    def get_by_item_name(item_name):
        return g.db_session.query(GreyItem).filter(
            GreyItem.is_deleted == 0,
            GreyItem.item_name == item_name
        ).first()

    @staticmethod
    def delete_by_item_id(item_id):
        g.db_session.query(GreyItem).filter(
            GreyItem.is_deleted == 0,
            GreyItem.item_id == item_id
        ).update({GreyItem.is_deleted: 1})

    @staticmethod
    def update_with_updated_time(item_id, item_data, item_type, visibility, version_id=None, updated_at=None):
        return g.db_session.query(GreyItem).filter(
            GreyItem.is_deleted == 0,
            GreyItem.item_id == item_id,
            GreyItem.updated_at == updated_at
        ).update({
            GreyItem.item_data: item_data,
            GreyItem.item_visibility: visibility,
            GreyItem.item_type: item_type,
            GreyItem.current_version_id: version_id
        },
        synchronize_session='fetch')
