# coding=utf-8

import pytest

from src.base import APIBase, QingCloudBase


@pytest.fixture
def api_base():
    base = APIBase()
    base.set_connection_timeout(15)
    base.set_socket_timeout(15)
    return base


@pytest.fixture
def qingcloud_base():
    base = QingCloudBase(
        access_key_id="QYACCESSKEYIDEXAMPLE",
        secret_access_key="SECRETACCESSKEY",
    )
    return base


def test_get(api_base):
    """测试 APIBase 基础类发送 get 请求"""
    params = {"foo": "bar"}
    resp = api_base._get("https://httpbin.org/get", params=params)

    assert resp["url"] == "https://httpbin.org/get?foo=bar"
    assert resp["args"] == params


def test_calc_signature(qingcloud_base):
    """ 测试计算签名字符串方法 QingCloudBase.calc_signature """
    params = {
        "count": 1,
        "vxnets.1": "vxnet-0",
        "zone": "pek1",
        "instance_type": "small_b",
        "signature_version": 1,
        "signature_method": "HmacSHA256",
        "instance_name": "demo",
        "image_id": "centos64x86a",
        "login_mode": "passwd",
        "login_passwd": "QingCloud20130712",
        "version": 1,
        "access_key_id": "QYACCESSKEYIDEXAMPLE",
        "action": "RunInstances",
        "time_stamp": "2013-08-27T14:30:10Z"
    }
    result = "32bseYy39DOlatuewpeuW5vpmW51sD1A%2FJdGynqSpP8%3D"
    assert result == qingcloud_base.calc_signature(params)
