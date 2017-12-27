# -*- coding: utf-8 -*-

from tests.api.commons.user import FakeUser
from tests.api.commons.privileges import FakePrivilege
from app.api.utils.privileges import get_users_for_privileges, get_privileges_for_resource
from app.api.models.user import User
from app.api.models.privilege import Privilege


def fake_user_get_by_ids(c, user_ids):
    return [FakeUser(user_id, "fake-user-"+str(user_id)) for user_id in user_ids]


def test_get_users_for_privileges_01():
    User.get_by_ids = classmethod(fake_user_get_by_ids)
    privileges = [FakePrivilege(1, 1, Privilege.Type.PULLER), FakePrivilege(2, 2, Privilege.Type.VIEWER), FakePrivilege(3, 3, Privilege.Type.MODIFIER)]
    user_dict = get_users_for_privileges(privileges)

    assert type(user_dict) == dict
    assert len(user_dict) == 3
    for k, v in user_dict.items():
        assert k == v.id


def fake_get_privileges_by_resource(res_id, resource_type):
    return [FakePrivilege(1, 1, Privilege.Type.PULLER), FakePrivilege(2, 2, Privilege.Type.VIEWER), FakePrivilege(3, 3, Privilege.Type.MODIFIER)]


def test_get_users_for_privileges_02():
    Privilege.get_privileges_by_resource = staticmethod(fake_get_privileges_by_resource)
    User.get_by_ids = classmethod(fake_user_get_by_ids)

    p_list = get_privileges_for_resource(1, 3)

    assert type(p_list) == list
    assert len(p_list) == 3
    for p in p_list:
        assert "id" in p
        assert "type" in p
        assert "user_id" in p
        assert "user_name" in p