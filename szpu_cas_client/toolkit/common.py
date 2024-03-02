import requests


def request_session():
    # 创建一个session
    session = requests.session()
    # proxy
    # session.proxies = {
    #     'http': 'http://127.0.0.1:8080',
    #     'https': 'http://127.0.0.1:8080'
    # }
    # session.verify = False
    # User-Agent
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/103.0.4606.81 Safari/537.36'
    })
    return session
