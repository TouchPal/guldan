# -*- coding: utf-8 -*-

from flask import Blueprint

users_blueprint = Blueprint("users", __name__)

from .search import users_search
