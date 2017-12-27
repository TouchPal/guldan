# -*- coding: utf-8 -*-
from app.async import send_dict


class DefaultAsyncSender(object):
    def send_dict(self, dict_message):
        pass


class GreyAsyncSender(object):
    def send_dict(self, dict_message):
        send_dict(dict_message)


def create_async_sender(op_info):
    if op_info.grey:
        return GreyAsyncSender()
    else:
        return DefaultAsyncSender()