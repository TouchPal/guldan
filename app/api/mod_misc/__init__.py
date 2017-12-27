# -*- coding: utf-8 -*-
from .login import login_blueprint
from .logout import logout_blueprint
from .register import register_blueprint


__all__ = [
    "login_blueprint",
    "logout_blueprint",
    "register_blueprint"
]