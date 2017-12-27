# -*- coding: utf-8 -*-
from flask import Blueprint

audit_blueprint = Blueprint("audit", __name__)

from .search import audit_search