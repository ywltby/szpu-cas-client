<h1 align="center">深圳职业技术大学CAS第三方客户端 👋</h1>
<p>
  <img alt="Version" src="https://img.shields.io/badge/version-1.0.0-blue.svg?cacheSeconds=2592000" />
  <a href="LICENSE" target="_blank">
    <img alt="License: LICENSE" src="https://img.shields.io/badge/License-LICENSE-yellow.svg" />
  </a>
</p>

> 使用 Python 优雅登录【深圳职业技术大学】的SSO统一身份认证平台，便捷地访问业务应用程序，
> 无需再重复造轮子。

## 🚫 免责声明
本程序仅对深职大SSO/CAS认证系统的接口进行了封装，作者不对程序的正确性或可靠性提供保证。 
请使用者自行判断具体场景是否适合使用该程序，使用该程序造成的问题或后果由使用者自行承担！

## ⚠ 温馨提示
在提出Issues或提交Pull requests切勿把暴露个人敏感信息，包括但不限于用户名，密码，学号，API Key等。
请勿使用edu邮箱提交任何PR！

## Install 
```sh
git clone https://github.com/HozukiKaede/szpu-cas-client
```
## Usage 

```python
from szpu_cas_client.cas import credential
from szpu_cas_client.app import app

# 用户名和密码认证CAS凭证
username = '21234567'
password = 'passwd1234@'
cas.cas_login(username, password)

# 认证业务系统
url = "https://i.szpt.edu.cn"
jwxt = app.app(app_url=url, cas_cred=cas)
response = jwxt.session.get('https://ehall.szpt.edu.cn/getLoginUser')
# 获取业务系统的API响应
print(response.json())

```

## Moudle

- 用户名（别名）和密码登录CAS
- 手机验证码登录CAS
- 通过缓存TGT票据的文件登录CAS
- 为业务应用颁发ST票据并获取业务应用的cookie(session对象)

## Author

👤 **HozukiKaede**

* Github: [@HozukiKaede](https://github.com/HozukiKaede/szpu-cas-client)

## 🤝 Contributing

欢迎贡献、问题和功能请求！<br />请随时检查 [issues page](https://github.com/HozukiKaede/szpu-cas-client/issues). 
您还可以查看 [contributing guide](https://github.com/HozukiKaede/szpu-cas-client/graphs/contributors).

## Show your support

Give a ⭐️ if this project helped you!

## 📝 License

Copyright © 2024 [HozukiKaede](https://github.com/HozukiKaede).<br />
This project is [LICENSE](https://github.com/HozukiKaede/szpu-cas-client/LICENSE) licensed.

***
_This README was generated with ❤️ by [readme-md-generator](https://github.com/kefranabg/readme-md-generator)_
