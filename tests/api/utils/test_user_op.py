# -*- coding: utf-8 -*-
import pytest
from app.api.utils.request_util import UserOperationInfo
from app.exc import GulDanException
from app.api.models.base import Resource
from app.api.models.item import Item
from app.api.models.privilege import Privilege


def test_set_parent_id():
    op_info = UserOperationInfo("111", "222")

    op_info.set_parent_id(123)
    assert op_info.parent_id == 123
    op_info.set_parent_id("123")
    assert op_info.parent_id == 123

    with pytest.raises(GulDanException) as e:
        op_info.set_parent_id("xxx")
    assert e.value.status_code == 400
    with pytest.raises(GulDanException) as e:
        op_info.set_parent_id("-123")
    assert e.value.status_code == 400
    with pytest.raises(GulDanException) as e:
        op_info.set_parent_id(None)
    assert e.value.status_code == 400


def test_set_visibility():
    op_info = UserOperationInfo("111", "222")

    op_info.set_visibility("true")
    assert op_info.visibility == Resource.Visibility.PRIVATE
    op_info.set_visibility("TRUE")
    assert op_info.visibility == Resource.Visibility.PRIVATE
    op_info.set_visibility("false")
    assert op_info.visibility == Resource.Visibility.PUBLIC
    op_info.set_visibility("FALSE")
    assert op_info.visibility == Resource.Visibility.PUBLIC

    with pytest.raises(GulDanException) as e:
        op_info.set_visibility(None)
    assert e.value.status_code == 400

    with pytest.raises(GulDanException) as e:
        op_info.set_visibility(123)
    assert e.value.status_code == 400

    with pytest.raises(GulDanException) as e:
        op_info.set_visibility("t")
    assert e.value.status_code == 400


def test_set_item_type():
    op_info = UserOperationInfo("111", "222")

    op_info.set_item_type(None)
    assert op_info.item_type == Item.Type.PLAIN
    op_info.set_item_type("plain")
    assert op_info.item_type == Item.Type.PLAIN
    op_info.set_item_type("PLAIN")
    assert op_info.item_type == Item.Type.PLAIN
    op_info.set_item_type("Plain")
    assert op_info.item_type == Item.Type.PLAIN

    op_info.set_item_type("json")
    assert op_info.item_type == Item.Type.JSON
    op_info.set_item_type("JSON")
    assert op_info.item_type == Item.Type.JSON
    op_info.set_item_type("Json")
    assert op_info.item_type == Item.Type.JSON

    op_info.set_item_type("xml")
    assert op_info.item_type == Item.Type.XML
    op_info.set_item_type("XML")
    assert op_info.item_type == Item.Type.XML
    op_info.set_item_type("xMl")
    assert op_info.item_type == Item.Type.XML

    op_info.set_item_type("yaml")
    assert op_info.item_type == Item.Type.YAML
    op_info.set_item_type("YAML")
    assert op_info.item_type == Item.Type.YAML
    op_info.set_item_type("Yaml")
    assert op_info.item_type == Item.Type.YAML

    with pytest.raises(GulDanException) as e:
        op_info.set_item_type("test")
    assert e.value.status_code == 400


def test_set_resource_name():
    op_info = UserOperationInfo("111", "222")

    op_info.set_resource_name("test")
    assert op_info.resource_name == "test"

    with pytest.raises(GulDanException) as e:
        op_info.set_resource_name(None)
    assert e.value.status_code == 400
    with pytest.raises(GulDanException) as e:
        op_info.set_resource_name("test@")
    assert e.value.status_code == 400
    with pytest.raises(GulDanException) as e:
        op_info.set_resource_name("")
    assert e.value.status_code == 400

    name_with_85_chars = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    op_info.set_resource_name(name_with_85_chars)
    assert op_info.resource_name == name_with_85_chars
    with pytest.raises(GulDanException) as e:
        op_info.set_resource_name(name_with_85_chars + "x")
    print(e.value.message)
    assert e.value.status_code == 403


def test_set_offset():
    op_info = UserOperationInfo("111", "222")

    op_info.set_offset(123)
    assert op_info.offset == 123

    with pytest.raises(GulDanException) as e:
        op_info.set_offset("123x")
    assert e.value.status_code == 400
    with pytest.raises(GulDanException) as e:
        op_info.set_offset(None)
    assert e.value.status_code == 400
    with pytest.raises(GulDanException) as e:
        op_info.set_offset("-123")
    assert e.value.status_code == 400


def test_set_limit():
    op_info = UserOperationInfo("111", "222")

    op_info.set_limit(123)
    assert op_info.limit == 123

    with pytest.raises(GulDanException) as e:
        op_info.set_limit("123x")
    assert e.value.status_code == 400
    with pytest.raises(GulDanException) as e:
        op_info.set_limit(None)
    assert e.value.status_code == 400
    with pytest.raises(GulDanException) as e:
        op_info.set_limit("-123")
    assert e.value.status_code == 400


def test_set_privilege_type():
    op_info = UserOperationInfo("111", "222")

    op_info.set_privilege_type("modifier")
    assert op_info.privilege_type == Privilege.Type.MODIFIER
    op_info.set_privilege_type("MODIFIER")
    assert op_info.privilege_type == Privilege.Type.MODIFIER
    op_info.set_privilege_type("MODIfier")
    assert op_info.privilege_type == Privilege.Type.MODIFIER
    op_info.set_privilege_type("viewer")
    assert op_info.privilege_type == Privilege.Type.VIEWER
    op_info.set_privilege_type("VIEWER")
    assert op_info.privilege_type == Privilege.Type.VIEWER
    op_info.set_privilege_type("VIewer")
    assert op_info.privilege_type == Privilege.Type.VIEWER
    op_info.set_privilege_type("puller")
    assert op_info.privilege_type == Privilege.Type.PULLER
    op_info.set_privilege_type("PULLER")
    assert op_info.privilege_type == Privilege.Type.PULLER
    op_info.set_privilege_type("pulLER")
    assert op_info.privilege_type == Privilege.Type.PULLER

    with pytest.raises(GulDanException) as e:
        op_info.set_privilege_type("test")
    assert e.value.status_code == 400
    with pytest.raises(GulDanException) as e:
        op_info.set_privilege_type("")
    assert e.value.status_code == 400
    with pytest.raises(GulDanException) as e:
        op_info.set_privilege_type(None)
    assert e.value.status_code == 400
