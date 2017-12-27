# -*- coding: utf-8 -*-
import logging
import logging.config
from logging.handlers import RotatingFileHandler


class GuldanLogHandler(RotatingFileHandler):
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=0):
        super(GuldanLogHandler, self).__init__(filename, mode, maxBytes, backupCount, encoding, delay)

    def format(self, record):
        msg = super(GuldanLogHandler, self).format(record)
        return msg.replace("\n", " #012")


class GuldanInfoFilter(logging.Filter):
    def filter(self, record):
        return record.levelno < logging.ERROR


class GuldanErrorFilter(logging.Filter):
    def filter(self, record):
        return record.levelno >= logging.ERROR


def gen_logging_config(app_config):
    info_file = "{path_prefix}/{app_name}.log".format(
        path_prefix=app_config.LOG_PATH_PREFIX,
        app_name=app_config.APP_NAME,
    )
    error_file = "{path_prefix}/{app_name}.error".format(
        path_prefix=app_config.LOG_PATH_PREFIX,
        app_name=app_config.APP_NAME,
    )
    audit_file = "{path_prefix}/{audit_file_name}.log".format(
        path_prefix=app_config.LOG_PATH_PREFIX,
        audit_file_name="{}_audit".format(app_config.APP_NAME)
    )
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'guldan_info_filter': {
                '()': GuldanInfoFilter
            },
            'guldan_error_filter': {
                '()': GuldanErrorFilter
            }
        },
        'root': {
            'handlers': ['error_file', 'info_file'],
            'level': 'INFO',
        },
        'loggers': {
            'app': {
                'handlers': ['error_file', 'info_file'],
                'propagate': False,
                'level': 'INFO',
            },
            app_config.APP_NAME+".audit": {
                'handlers': ['error_file', 'audit'],
                'propagate': False,
                'level': 'INFO',
            },
            'sqlalchemy.pool': {
                'handlers': ['error_file', 'info_file'],
                'propagate': False,
                'level': 'INFO',
            }
        },
        'handlers': {
            'info_file': {
                'level': 'INFO',
                'class': 'app.log.GuldanLogHandler',
                'formatter': 'guldan',
                'filters': ['guldan_info_filter'],
                'filename': info_file,
                'encoding': 'utf8',
                'maxBytes': 2147483648,  # 2GB by default
                'backupCount': 5
            },
            'error_file': {
                'level': 'INFO',
                'class': 'app.log.GuldanLogHandler',
                'formatter': 'guldan',
                'filters': ['guldan_error_filter'],
                'filename': error_file,
                'encoding': 'utf8',
                'maxBytes': 2147483648, # 2GB by default
                'backupCount': 5
            },
            'audit': {
                'level': 'INFO',
                'class': 'app.log.GuldanLogHandler',
                'formatter': 'guldan',
                'filters': ['guldan_info_filter'],
                'filename': audit_file,
                'encoding': 'utf8',
                'maxBytes': 2147483648,  # 2GB by default
                'backupCount': 5
            }
        },
        'formatters': {
            'guldan': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        }
    }


def init_logging(app_config):
    conf = gen_logging_config(app_config)

    logging.config.dictConfig(conf)
