# coding=utf-8

import hmac
import base64
from datetime import datetime
from urllib.parse import urlencode, quote, urlsplit
from functools import partialmethod
from json import JSONDecodeError

import requests
from requests.exceptions import ReadTimeout, ConnectTimeout


class APIBase(object):
    """ 自定义web请求类，封装requests """
    def __init__(self):
        self.__connect_timeout = 5.0
        self.__socket_timeout = 5.0
        self.__proxies = {}

    def set_connection_timeout(self, second):
        """设置请求超时时间，单位秒"""
        self.__connect_timeout = second

    def set_socket_timeout(self, second):
        """设置响应超时时间，单位秒"""
        self.__socket_timeout = second

    def set_proxies(self, proxies):
        """设置代理"""
        self.__proxies = proxies

    def _request(self, method, url, params=None, data=None, json=None, **kw):
        """自定义请求"""
        try:
            resp = requests.request(
                method.upper().strip(),
                url,
                params=params,
                data=data,
                json=json,
                timeout=(self.__connect_timeout, self.__socket_timeout),
                proxies=self.__proxies,
                **kw
            )
            data = resp.json()
        except (ReadTimeout, ConnectTimeout):
            return {
                "errcode": "sdk001",
                "errmsg": "connection or read data timeout",
            }
        except JSONDecodeError:
            return {
                "errcode": "sdk002",
                "errmsg": "invalid json data",
            }
        return data

    _get = partialmethod(_request, "GET")
    _post = partialmethod(_request, "POST")
    _put = partialmethod(_request, "PUT")
    _delete = partialmethod(_request, "DELETE")


class QingCloudBase(APIBase):
    """ 青云 Base 类，包括生成签名参数和请求 """
    def __init__(self, qy_access_key_id, qy_secret_access_key):
        """ 传入 API 密钥的 ID（access_key_id）和私钥（secret_access_key）"""
        super(QingCloudBase, self).__init__()
        self.access_key_id = qy_access_key_id
        self.secret_access_key = qy_secret_access_key
        self.url = "https://api.qingcloud.com/iaas/"

    def calc_signature(self, params, http_method="GET", digestmod="SHA256"):
        """计算请求签名"""
        # 1. 按参数名进行升序排列
        params = sorted(params.items())

        # 2. 对参数名称和参数值进行URL编码，编码时空格要转换成 “%20” , 而不是 “+”
        # 3. 构造URL请求
        params = urlencode(params, quote_via=quote)

        # 4. 构造被签名串
        path = urlsplit(self.url).path
        method = http_method.upper()
        string_to_sign = "\n".join([method, path, params])

        # 5. 计算签名

        # 5.1 将 secret_access_key 作为key，生成 HMAC-SHA256 或者 HMAC-SHA1 签名
        h = hmac.new(
            key=self.secret_access_key.encode(),
            msg=string_to_sign.encode(),
            digestmod=digestmod,
        )

        # 5.2 将签名进行 Base64 编码
        signature = base64.b64encode(h.digest()).decode()

        # 5.3 将 Base64 编码后的结果进行 URL 编码，末尾存在空格时，直接将空格转为 “+”
        # 这一步省略，requests 对 get 请求参数会自动进行 URL 编码

        return signature

    def get(self, params):
        """发起 API 接口请求"""
        common_params = {
            "time_stamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "access_key_id": self.access_key_id,
            "version": 1,
            "signature_method": "HmacSHA256",
            "signature_version": 1,
        }
        # 使用户输入可以更新公共参数配置
        common_params.update(params)
        params = common_params

        # 计算签名
        params["signature"] = self.calc_signature(params)

        # 发起请求
        response = self._get(self.url, params)

        return response
