# -*- coding: utf-8 -*-

from app.api.models.base import Resource
from app.api.models.item import Item
from app.api.models.project import Project
from app.api.models.privilege import Privilege
from app.exc import GulDanException
from app.cache import cache
from app.api.mod_puller.pull import pull_item
from app.api.mod_puller.puller import ItemPuller
from app.api.utils.request_util import parse_request
from app.kv import get_kv_manager

TARGET_PRIVILEGES_TYPES_FOR_ITEM = [Privilege.Type.PULLER, Privilege.Type.VIEWER, Privilege.Type.MODIFIER]
TARGET_PRIVILEGES_TYPES_FOR_PROJECT = [Privilege.Type.MODIFIER]
TARGET_PRIVILEGES_TYPES_FOR_ORG = [Privilege.Type.MODIFIER]


def ensure_item(item_id):
    item = Item.get_by_id(item_id)
    if not item:
        raise GulDanException().with_code(404).with_message(
            u"找不到配置项(id:{})".format(item_id)
        )

    return item


def ensure_item_by_name(item_name):
    item = Item.get_by_name(item_name)
    if not item:
        raise GulDanException().with_code(404).with_message(
            u"找不到配置项(name:{})".format(item_name)
        )

    return item


def get_user_hash_for_item(item_id):
    item_user_hashes = Privilege.get_user_hash_for_resource(item_id, Resource.Type.ITEM, TARGET_PRIVILEGES_TYPES_FOR_ITEM)
    project_id = Item.get_parent_id(item_id)
    project_user_hashes = Privilege.get_user_hash_for_resource(project_id, Resource.Type.PROJECT, TARGET_PRIVILEGES_TYPES_FOR_PROJECT)
    org_id = Project.get_parent_id(project_id)
    org_user_hashes = Privilege.get_user_hash_for_resource(org_id, Resource.Type.ORG, TARGET_PRIVILEGES_TYPES_FOR_ORG)

    user_hashes = set()
    for uh in item_user_hashes + project_user_hashes + org_user_hashes:
        user_hashes.add(uh[0])

    return user_hashes


def get_user_hash_from_db(item_id, visibility):
    user_hashes = get_user_hash_for_item(item_id)
    if visibility == Resource.Visibility.PUBLIC:
        user_hashes.add(None)

    return user_hashes


def get_normal_fetcher_hash_from_kv(item_name):
    user_hashes = set()
    for normal_fetcher in get_kv_manager().get_item_normal_fetchers(item_name):
        user_hashes.add(normal_fetcher.get("puller_hash", None))

    return user_hashes


def get_normal_fetcher_hash_under_item(item_id, item_name, visibility):
    user_hashes_from_kv = get_normal_fetcher_hash_from_kv(item_name)
    user_hashes_from_db = get_user_hash_from_db(item_id, visibility)

    return user_hashes_from_kv | user_hashes_from_db


def invalidate_cache(item_id, item_name, visibility):
    user_hash_set = get_normal_fetcher_hash_under_item(item_id, item_name, visibility)
    puller = ItemPuller(item_name)
    for user_hash in user_hash_set:
        cache.delete_memoized(pull_item, puller, item_name, user_hash)


def parse_item_options_base(request):
    op_info = parse_request(request)

    grey_option = request.args.get("grey", "false")
    lower_grey_option = str(grey_option).lower()
    if lower_grey_option == "false":
        op_info.grey = False
    elif lower_grey_option == "true":
        op_info.grey = True
    else:
        raise GulDanException().with_code(404).with_message(
            u"grey选项应该是一个bool"
        )

    return op_info
