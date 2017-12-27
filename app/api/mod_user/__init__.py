# -*- coding: utf-8 -*-
from flask import Blueprint

user_blueprint = Blueprint("user", __name__)

from .modify import user_modify
