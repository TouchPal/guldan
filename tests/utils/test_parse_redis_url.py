# -*- coding: utf-8 -*-
from __future__ import print_function
import pytest
from app.utils import parse_redis_url
from app.exc import GulDanException


def test_parse_redis_url_01():
    host, port, db = parse_redis_url("redis://127.0.0.1:16379/1")
    assert host == "127.0.0.1"
    assert port == 16379
    assert db == 1


def test_parse_redis_url_02():
    with pytest.raises(GulDanException) as e:
        host, port, db = parse_redis_url("mysql://127.0.0.1:16379/1")

    assert e.value.status_code == 500


def test_parse_redis_url_03():
    with pytest.raises(GulDanException) as e:
        parse_redis_url("redis://127.0.0.1:ss/1")

    assert e.value.status_code == 500

    with pytest.raises(GulDanException) as e:
        parse_redis_url("redis://127.0.0.1:163ss/1")

    assert e.value.status_code == 500

    with pytest.raises(GulDanException) as e:
        parse_redis_url("redis://127.0.0.1:/1")

    assert e.value.status_code == 500


def test_parse_redis_url_04():
    with pytest.raises(GulDanException) as e:
        parse_redis_url("redis://127.0.0.1:123/s")

    assert e.value.status_code == 500