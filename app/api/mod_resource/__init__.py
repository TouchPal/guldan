# -*- coding: utf-8 -*-
from flask import Blueprint

resource_blueprint = Blueprint("resource", __name__)

from .search import resource_search


