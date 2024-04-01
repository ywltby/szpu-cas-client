import os
import json
import time
import random
import requests
import execjs
from lxml import etree
from loguru import logger
from szpu_cas_client.toolkit.common import request_session
from szpu_cas_client.toolkit.decrypt_sliding_verification import SlidingVerification


# 创建认证客户端类,request库的封装成 session
class ClientAuth:
    def __init__(self, domain="https://authserver.szpu.edu.cn", debug: bool = False):
        self.domain = domain
        self.username = None
        self.password = None
        self.debug = debug
        self.session: requests.session = request_session()
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        # self.app: app = app
        self.mobile = None
        self.required_cookie = self.get_required_cookie()
        self.cas_cookie = None
        self.logged_in = False

    def get_required_cookie(self):
        # GET请求获取Cas登录前必须的 Cookie 还有一些隐藏的参数
        url = self.domain + '/authserver/login'
        response = self.session.get(url)
        if response.status_code != 200:
            raise Exception('获取登录前必须的 Cookie 失败')
        lxml_response = etree.HTML(response.text)
        # 获取form标签下所有input的参数
        form_class = lxml_response.xpath('//*[@id="pwdFromId"]')
        form_data = {}
        for input in form_class[0].xpath('//input'):
            # 整个存入转换成字典
            attrib_dict = {key: value for key, value in input.items()}
            # 如果有value属性就存入字典,且name属性作为key，name 重复就覆盖 value
            if 'id' in attrib_dict and 'value' in attrib_dict:
                form_data[attrib_dict['id']] = attrib_dict['value']
        return form_data

    def crypto_password(self, password: str, key: str):
        # 直接调用js文件劫持加密password，解决各种换参数的愚蠢问题
        url = "/authserver/szptThemegs/static/common/encrypt.js"
        js_code = self.session.get(self.domain + url).text
        ctx = execjs.compile(js_code)
        # 调用js文件中的方法
        return ctx.call('encryptAES', password, key)

    def check_captcha(self):
        # 检查是否需要验证码
        url = self.domain + '/authserver/checkNeedCaptcha.htl'
        response = self.session.get(url=url, params={'username': self.username}).json()
        if response['isNeed'] is True:
            logger.error('需要验证码')
            status = self.decrypt_captcha()
            if status:
                return True
            raise Exception('自动化绕过验证码失败，请手动输入验证码')

    def decrypt_captcha(self):
        # 尝试三次自动识别验证码
        for _ in range(3):
            # 获取滑动验证码参数
            url = self.domain + '/authserver/common/openSliderCaptcha.htl'
            params = {'_': str(int(time.time() * 1000))}
            response = self.session.get(url=url, params=params).json()
            small_image_base64 = response['smallImage']
            big_image_base64 = response['bigImage']
            decrypt = SlidingVerification()
            decrypt = decrypt.decrypt(small_image_base64, big_image_base64)
            canvas_length = decrypt['canvasLength']
            # 添加一定的偏移量 防止被识别为机器人
            move_length = decrypt['moveLength'] + random.randint(1, 5)
            logger.debug('验证码宽度:', canvas_length)
            logger.debug('滑动距离:', move_length)
            # 提交滑动验证码
            url = self.domain + '/authserver/common/verifySliderCaptcha.htl'
            data = {'canvasLength': canvas_length, 'moveLength': move_length}
            response = self.session.post(url, data=data).json()
            if response['errorCode'] == 1 and response['errorMsg'] == 'success':
                logger.info('验证码自动验证通过')
                return True
        logger.error('尝试验证码自动验证失败')
        return False

    def login(self, username, password):
        self.username = username
        self.password = password
        # 登录
        url = self.domain + '/authserver/login'
        form_data = self.required_cookie
        self.check_captcha()
        crypt_password = self.crypto_password(self.password, form_data['pwdEncryptSalt'])
        form_data.update({
            'username': self.username,
            'password': crypt_password,
            'captcha': '',
            '_eventId': form_data['_eventId'],
            'cllt': form_data['cllt'],
            'dllt': form_data['dllt'],
            'lt': form_data['lt'],
            'execution': form_data['execution']
        })
        response = self.session.post(url, data=form_data, allow_redirects=False)

        if response.status_code != 302:
            show_error_tip_class = etree.HTML(response.text).xpath('//*[@id="showErrorTip"]//text()')
            if show_error_tip_class:
                raise Exception(show_error_tip_class[0])
            else:
                raise Exception('登录失败，未知错误，请查看 log 文件')
        # 获取登录后的Cookie
        # print(self.session.cookies.get_dict())
        self.cas_cookie = self.session.cookies.get_dict()
        self.logged_in = True
        return self.session.cookies.get_dict()

    def login_sms_send(self, mobile):
        # 发送短信验证码
        self.mobile = mobile
        # 先自动滑动验证码
        self.decrypt_captcha()
        # 发送短信验证码
        url = self.domain + '/authserver/dynamicCode/getDynamicCode.htl'
        # /authserver/szptThemegs/static/web/js/login.js 默认密钥
        mobile_encrypt = self.crypto_password(mobile, 'rjBFAaHsNkKAhpoi')
        data = {'mobile': mobile_encrypt,'captcha':''}
        response = self.session.post(url, data=data).json()
        logger.debug(response)
        if response['code'] == 'success':
            logger.info('短信验证码发送成功')
            return True
        else:
            logger.info('短信验证码发送失败')
            return False

    def login_sms(self, sms_code):
        # 短信方式登录
        url = self.domain + '/authserver/login'
        form_data = self.required_cookie
        form_data.update({
            'username': self.mobile,
            'dynamicCode': sms_code,
            'captcha': '',
            '_eventId': form_data['_eventId'],
            'cllt': 'dynamicLogin',
            'dllt': 'generalLogin',
            'lt': form_data['lt'],
            'execution': form_data['execution']
        })
        response = self.session.post(url, data=form_data, allow_redirects=False)

        if response.status_code != 302:
            show_error_tip_class = etree.HTML(response.text).xpath('//*[@id="showErrorTip"]//text()')
            if show_error_tip_class:
                raise Exception(show_error_tip_class[0])
            else:
                raise Exception('登录失败，未知错误，请查看 log 文件')
        # 获取登录后的Cookie
        # print(self.session.cookies.get_dict())
        self.cas_cookie = self.session.cookies.get_dict()
        self.logged_in = True
        return self.session.cookies.get_dict()

    def load_cookie(self, cookie: dict):
        self.cas_cookie = cookie
        self.session.cookies.update(cookie)
        self.logged_in = True

    def app_login(self, service_url: str):
        if self.logged_in is False:
            raise Exception('cas未登录')
        url = self.domain + '/authserver/login'
        params = {
            'service': service_url}
        response = self.session.get(url, params=params, allow_redirects=False)
        if response.status_code != 302:
            raise Exception('App登录失败')
        location = response.headers['Location']
        st = location.split('ticket=')[-1]
        # print(st)
        # 返回登录成功的session对象、app登录的回调地址、app的st
        return location, st

    def __del__(self):
        # 调用结束后把登录成功的cookie保存到文件
        if self.logged_in:
            with open('cas_cookie.json', 'w') as f:
                f.write(json.dumps(self.cas_cookie))

