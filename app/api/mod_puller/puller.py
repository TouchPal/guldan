# -*- coding: utf-8 -*-
import logging
import time

from app.api.models.base import Resource
from app.api.models.item import Item
from app.api.models.item import GreyItem
from app.api.models.version import ResourceVersion
from app.exc import GulDanException
from app.async import send_dict

logger = logging.getLogger(__name__)


def ensure_item_by_name(item_name):
    item = Item.get_by_name(item_name)
    if not item:
        raise GulDanException().with_code(404).with_message(
            u"找不到配置项(name:{})".format(item_name)
        )

    return item


def ensure_grey_item_by_name(item_name):
    grey_item = GreyItem.get_by_item_name(item_name)
    if not grey_item:
        raise GulDanException().with_code(404).with_message(
            u"找不到配置项(name:{})的灰度版本".format(item_name)
        )

    return grey_item


class Puller(object):
    def __init__(self, item_name):
        self.item_name = item_name

    def send_async_message(self, op_info, request):
        send_dict({
            "remote_addr": request.remote_addr,
            "puller_hash": op_info.user_hash,
            "item_name": self.item_name,
            "iver": op_info.item_version,
            "grey": op_info.grey,
            "cid": op_info.cid,
            "cver": op_info.cver,
            "ctype": op_info.ctype,
            "lver": op_info.lver,
            "pull_time": int(time.time())
        })


class ItemPuller(Puller):
    def __init__(self, item_name):
        super(ItemPuller, self).__init__(item_name)
        self.item_name = item_name

    def __str__(self):
        return "ItemPuller"

    def pull(self, item_full_name):
        item = ensure_item_by_name(item_full_name)

        return {
            "id": item.id,
            "content": item.data,
            "version_id": item.current_version_id,
            "timestamp": int(time.mktime(item.updated_at.timetuple())),
            "visibility": item.visibility
        }


class VersionPuller(Puller):
    def __init__(self, item_name, version_id):
        super(VersionPuller, self).__init__(item_name)
        self.version_id = version_id

    def __str__(self):
        return "VersionPuller(version_id:{})".format(self.version_id)

    def pull(self, item_full_name):
        item = ensure_item_by_name(item_full_name)

        resource_version = ResourceVersion.get_by_version(item.id, Resource.Type.ITEM, self.version_id)
        if not resource_version:
            raise GulDanException().with_code(404).with_message(
                u"找不到版本为({})的配置项{}".format(self.version_id, item_full_name)
            )

        return {
            "id": item.id,
            "content": resource_version.resource_content,
            "version_id": self.version_id,
            "timestamp": int(time.mktime(resource_version.updated_at.timetuple())),
            "visibility": item.visibility
        }


class ItemGreyPuller(Puller):
    def __init__(self, item_name):
        super(ItemGreyPuller, self).__init__(item_name)

    def __str__(self):
        return "ItemGreyPuller"

    def pull(self, item_full_name):
        grey_item = ensure_grey_item_by_name(item_full_name)

        return {
            "id": grey_item.item_id,
            "content": grey_item.item_data,
            "version_id": grey_item.current_version_id,
            "timestamp": int(time.mktime(grey_item.updated_at.timetuple())),
            "visibility": grey_item.item_visibility
        }


def create_puller(op_info, item_full_name):
    if op_info.grey:
        return ItemGreyPuller(item_full_name)
    elif op_info.version_id:
        return VersionPuller(item_full_name, op_info.version_id)
    else:
        return ItemPuller(item_full_name)
