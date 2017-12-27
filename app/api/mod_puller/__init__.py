# -*- coding: utf-8 -*-
from flask import Blueprint


puller_blueprint = Blueprint("puller", __name__)


from .pull import pull_config