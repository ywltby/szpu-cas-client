import json

from szpu_cas_client.toolkit import common
from szpu_cas_client.cas import credential
from urllib.parse import unquote


class app:
    def __init__(self, app_url, cas_cred):
        self.domain = app_url
        self.session = common.request_session()
        self.cas_cred: credential = cas_cred
        self.login()

    def login(self):
        # 获取cas的service跳转链接
        response = self.session.get(self.domain)
        service_url = unquote(response.url.split('service=')[1])
        # 登录获得app cookie(st)
        location, st = self.cas_cred.app_login(service_url)
        # 请求一次app的service跳转链接，获得app的cookie
        self.session.get(location)


