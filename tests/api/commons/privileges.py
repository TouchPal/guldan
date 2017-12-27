# -*- coding: utf-8 -*-


class FakePrivilege(object):
    def __init__(self, id, user_id, privilege_type):
        self.id = id
        self.user_id = user_id
        self.privilege_type = privilege_type
