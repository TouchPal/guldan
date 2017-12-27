# -*- coding: utf-8 -*-
import re
from app.exc import GulDanException


def parse_redis_url(url):
    m = re.match("redis://(.+?):(\d+?)/(\d+)", url)
    if not m or not m.groups():
        raise GulDanException().with_code(500).with_message(
            u"非法的redis地址:{}".format(url)
        )
    groups = m.groups()
    return groups[0], int(groups[1]), int(groups[2])
