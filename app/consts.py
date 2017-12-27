# -*- coding: utf-8 -*-
import socket

HOSTNAME = socket.getfqdn()

ZK_PATH_PREFIX = "/touchpal/config"
MAX_ID_LIST_LENGTH = 1000
GULDAN_VERSION_STR = "X-Guldan-Version"
GULDAN_TYPE_STR = "X-Guldan-Type"
GULDAN_TOKEN_STR = "X-Guldan-Token"
GULDAN_SESSION_ID_STR = "X-Guldan-Session-Id"
MAX_RESOURCE_NAME_LENGTH = 85
GULDAN_EXC_METRICS_NAME = "guldan.exc"

ITEM_VERSION_SEQUENCE_NAME = "item_version_id"
GREY_ITEM_VERSION_SEQUENCE_NAME = "grey_item_version_id"
