# -*- coding: utf-8 -*-
import logging

from flask import Flask

from app.exc import GulDanException

app = Flask(__name__, template_folder="static/templates")
app_config = None


def load_flask_config():
    from config import FlaskConfig
    app.config.from_object(FlaskConfig)


def register_api():
    from api import mod_misc
    from api import mod_user
    from api import mod_users
    from api import mod_org
    from api import mod_project
    from api import mod_item
    from api import mod_puller
    from api import mod_resource
    from api import mod_audit

    app.register_blueprint(mod_misc.login_blueprint, url_prefix="/api")
    app.register_blueprint(mod_misc.logout_blueprint, url_prefix="/api")
    app.register_blueprint(mod_misc.register_blueprint, url_prefix="/api")
    app.register_blueprint(mod_user.user_blueprint, url_prefix="/api/user")
    app.register_blueprint(mod_users.users_blueprint, url_prefix="/api/users")
    app.register_blueprint(mod_org.org_blueprint, url_prefix="/api/org")
    app.register_blueprint(mod_project.project_blueprint, url_prefix="/api/project")
    app.register_blueprint(mod_item.item_blueprint, url_prefix="/api/item")
    app.register_blueprint(mod_puller.puller_blueprint, url_prefix="/api/puller")
    app.register_blueprint(mod_resource.resource_blueprint, url_prefix="/api/resource")
    app.register_blueprint(mod_audit.audit_blueprint, url_prefix="/api/audit")


def register_webpage_url():
    from webpage_handlers import index


def load_app_config():
    global app_config
    if app_config is None:
        from config import AppConfig
        app_config = AppConfig()
        app_config.refresh_configs()

    return app_config


def init_logging(app_config):
    from log import init_logging
    init_logging(app_config)


def force_use_http_1_1():
    from werkzeug.serving import WSGIRequestHandler
    WSGIRequestHandler.protocol_version = "HTTP/1.1"


def init_request_ctx():
    from request import init_admin_user, add_db_session, db_ending


def init_kafka():
    from app.async.kafka import init_kafka_manager
    app_config = load_app_config()
    init_kafka_manager(app_config.KAFKA_BROKERS, app_config.KAFKA_ZK, app_config.KAFKA_ITEM_GREY_TOPIC, app_config.KAFKA_VERSION)


def init_cache():
    from app.cache import get_cache_manager
    get_cache_manager()


def init():
    load_app_config()
    init_logging(app_config)
    init_cache()
    init_kafka()
    load_flask_config()
    register_api()
    register_webpage_url()
    force_use_http_1_1()
    init_request_ctx()

    logger = logging.getLogger(__name__)
    logger.info("{} finished starting".format(app_config.APP_NAME))

