# -*- coding: utf-8 -*-
from app.api.models.org import Org
from app.exc import GulDanException


def ensure_org(org_id):
    org = Org.get_by_id(org_id)
    if not org:
        raise GulDanException().with_code(404).with_message(u"找不到组织(id:{})".format(org_id))

    return org