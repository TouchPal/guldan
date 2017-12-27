# -*- coding: utf-8 -*-
from logging.handlers import RotatingFileHandler


class GuldanLogHandler(RotatingFileHandler):
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=0):
        super(GuldanLogHandler, self).__init__(filename, mode, maxBytes, backupCount, encoding, delay)

    def format(self, record):
        msg = super(GuldanLogHandler, self).format(record)
        return msg.replace("\n", " #012")


