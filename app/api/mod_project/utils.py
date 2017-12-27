# -*- coding: utf-8 -*-

from app.api.models.project import Project
from app.exc import GulDanException


def ensure_project(project_id):
    project = Project.get_by_id(project_id)
    if not project:
        raise GulDanException().with_code(404).with_message(u"找不到项目(id:{})".format(project_id))

    return project
