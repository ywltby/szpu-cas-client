# Description: 测试CAS认证和业务系统认证
# Author: HozukiKaede
# 深圳职业技术大学CAS第三方Python SDK

from szpu_cas_client.cas import credential
from szpu_cas_client.app import app
import json

cas = credential.ClientAuth()

# 用户名和密码认证CAS凭证
username = '21234567'
password = 'passwd1234@'
cas.login(username, password)

# 手机验证码认证CAS凭证
# mobile = "13800138000"
# cas.login_sms_send(mobile)
# cas.login_sms(input('请输入验证码：'))

# 读取文件中的CAS凭证
# cas_cookie = json.loads(open('cas_cookie.json', 'r').read())
# cas.load_cookie(cas_cookie)


# 认证业务系统
url = "https://i.szpt.edu.cn"
jwxt = app.app(app_url=url, cas_cred=cas)
response = jwxt.session.get('https://ehall.szpt.edu.cn/getLoginUser')
# 获取业务系统的API响应
print(response.json())
