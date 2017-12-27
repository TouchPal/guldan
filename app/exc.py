# -*- coding: utf-8 -*-


class GulDanException(Exception):
    def __init__(self):
        super(Exception, self).__init__()
        self.status_code = 500
        self.message = u"服务器内部错误"

    def with_message(self, message):
        self.message = message
        return self

    def with_code(self, code):
        self.status_code = code
        return self

    def to_dict(self):
        return {
            "status_code": self.status_code,
            "msg": self.message
        }


class NotLoginException(GulDanException):
    def __init__(self):
        super(NotLoginException, self).__init__()
