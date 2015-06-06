# -*- coding: utf-8 -*-

__author__ = 'abstractcat'

import urllib
import urllib2
import base64
import re
import hashlib
import json
import binascii
import time
import random
import urlparse
import cookielib
import chardet
import rsa
from abstractcat.login import captcha



# import cStringIO
# from PIL import Image


def request_url(url):
    '''
    Request url, raise exception when failed.
    :param url:
    :return:
    '''

    # try serval times
    retry = 2
    for i in range(0, retry):
        try:
            data = urllib2.urlopen(url,timeout=10).read()
            return data
        except Exception as e:
            print 'Exception info:', e
    print 'Failed to request for %s times, login aborted!' % retry
    raise Exception('request_url')


def get_prelogin_status(username):
    '''
    Perform prelogin action, raise exception when failed.
    :param username:
    :return:
    '''
    prelogin_url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=' + get_user(
        username) + \
                   '&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.18)&_=' + str(time.time()).replace('.', '')

    data = request_url(prelogin_url)

    try:
        p = re.compile('\((.*)\)')
        json_data = p.search(data).group(1)
        data = json.loads(json_data)
        servertime = str(data['servertime'])
        nonce = data['nonce']
        rsakv = data['rsakv']
        showpin = data['showpin']
        pcid = data['pcid']
        return servertime, nonce, rsakv, showpin, pcid
    except Exception as e:
        print 'Error occured for getting prelogin status!'
        print 'Data received:', data
        print 'Exception info:', e
        raise Exception('get_prelogin_status')


def login(uname, pwd, address):
    '''
    Login and return cookie, raise exception when failed.
    :param uname:
    :param pwd:
    :param address:
    :return:
    '''
    login_data = {
        'entry': 'weibo',
        'gateway': '1',
        'from': '',
        'savestate': '7',
        'userticket': '1',
        'pagerefer': '',
        'vsnf': '1',
        'su': '',
        'service': 'miniblog',
        'servertime': '',
        'nonce': '',
        'pwencode': 'rsa2',
        'rsakv': '',
        'sp': '',
        'encoding': 'UTF-8',
        'prelt': '45',
        'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
        'returntype': 'META',
        'pcid': '',
        'door': ''
    }
    cookie_jar = cookielib.LWPCookieJar()
    cookie_support = urllib2.HTTPCookieProcessor(cookie_jar)
    proxy = urllib2.ProxyHandler({'http': address})
    opener = urllib2.build_opener(cookie_support, proxy)
    # set opener as global
    urllib2.install_opener(opener)
    login_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'

    # get prelogin status
    servertime, nonce, rsakv, showpin, pcid = get_prelogin_status(uname)

    # Fill POST data
    login_data['servertime'] = servertime
    login_data['nonce'] = nonce
    login_data['su'] = get_user(uname)
    login_data['sp'] = get_pwd_rsa(pwd, servertime, nonce)
    login_data['rsakv'] = rsakv
    # use dll to identify pin
    if showpin == 1:
        print 'Pin required for login.'

        login_data['pcid'] = pcid
        s = random_number()
        pin_url = 'http://login.sina.com.cn/cgi/pin.php?s=%s&p=%s' % (s, pcid)

        # download the pin image
        pin_data = request_url(pin_url)

        # show image
        # file = cStringIO.StringIO(pin_data)
        # img = Image.open(file)
        # img.show()

        # call captcha to resolve pin
        pin = captcha.resolve(pin_data)
        login_data['door'] = pin
        print 'Pin resolved:%s.' % pin

    login_data = urllib.urlencode(login_data)

    http_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.65 Safari/537.36'}
    req_login = urllib2.Request(
        url=login_url,
        data=login_data,
        headers=http_headers
    )

    result = request_url(req_login)
    print(result)
    try:
        text = auto_decode(result)
    except Exception as e:
        print 'Error occured for decoding post response!'
        print 'Data received:', result
        print 'Exception info:', e
        raise Exception('login')

    try:
        # search for redirect url
        p = re.compile('location\.replace\([\'"](.*?)[\'"]\)')
        redirect_url = p.search(text).group(1).encode('ascii')
        redirect_args = urlparse.parse_qs(redirect_url)
        print('redirect_url:' + redirect_url)
    except Exception as e:
        print 'Error occured for getting redirect url!'
        print 'Data received:', text
        print 'Exception info:', e
        raise Exception('login')

    # check if reason in redirect url is not empty, login must be failed
    if 'reason' in redirect_args:
        # get reason
        try:
            reason = redirect_args['reason'][0]
            reason = auto_decode(reason)
            print 'Login failed, reason is:%s!' % reason
        except Exception as e:
            print 'Error occured for decode reason!'
            print 'Exception info:', e
            raise Exception('login')

        if reason == u'输入的验证码不正确':
            return login(uname, pwd, address)
        else:
            raise Exception('login')

    # get url feedback to finally confirm login status
    data = request_url(redirect_url)
    data = auto_decode(data)
    try:
        patt_feedback = 'parent.sinaSSOController.feedBackUrlCallBack\((.*?)\)'
        p = re.compile(patt_feedback, re.MULTILINE)
        feedback = p.search(data).group(1)
        feedback_json = json.loads(feedback)
    except Exception as e:
        print 'Error occured for finally confirm login status!'
        print 'Data received:', data
        print 'Exception info:', e

        raise Exception('login')

    if feedback_json['result']:
        cookie_dict = dict()
        for ck in cookie_jar:
            cookie_dict[ck.name] = ck.value
        return str(cookie_dict)
    else:
        reason = feedback_json['reason']
        print 'Finally confirm login status failed, Reason is %s!' % reason
        print 'Data received:', data

        raise Exception('login')


def create_cookie(uname, pwd, address):
    '''
    Create cookie, return cookie and status code
    status  meaning
    0       ok
    1       failed in request_url function
    2       failed in get_prelogin_status function
    3       failed in login function
    :param uname:
    :param pwd:
    :param address:
    :return:
    '''
    print 'Create cookie with (%s,%s,%s)' % (uname, pwd, address)
    try:
        cookie = login(uname, pwd, address)
        return (cookie, 0)
    except Exception as e:
        print 'Failed to create cookie!'
        print 'Exception raised by function:', e
        if e.message == 'request_url':
            return (None, 1)
        elif e.message == 'get_prelogin_status':
            return (None, 2)
        elif e.message == 'login':
            return (None, 3)
        else:
            return (None, 4)


def get_pwd_wsse(pwd, servertime, nonce):
    """
        Get wsse encrypted password
    """
    pwd1 = hashlib.sha1(pwd).hexdigest()
    pwd2 = hashlib.sha1(pwd1).hexdigest()
    pwd3_ = pwd2 + servertime + nonce
    pwd3 = hashlib.sha1(pwd3_).hexdigest()
    return pwd3


def get_pwd_rsa(pwd, servertime, nonce):
    """
        Get rsa2 encrypted password, using RSA module from https://pypi.python.org/pypi/rsa/3.1.1, documents can be accessed at
        http://stuvel.eu/files/python-rsa-doc/index.html
    """
    # n, n parameter of RSA public key, which is published by WEIBO.COM
    # hardcoded here but you can also find it from values return from prelogin status above
    weibo_rsa_n = 'EB2A38568661887FA180BDDB5CABD5F21C7BFD59C090CB2D245A87AC253062882729293E5506350508E7F9AA3BB77F4333231490F915F6D63C55FE2F08A49B353F444AD3993CACC02DB784ABBB8E42A9B1BBFFFB38BE18D78E87A0E41B9B8F73A928EE0CCEE1F6739884B9777E4FE9E88A1BBE495927AC4A799B3181D6442443'

    # e, exponent parameter of RSA public key, WEIBO uses 0x10001, which is 65537 in Decimal
    weibo_rsa_e = 65537
    message = str(servertime) + '\t' + str(nonce) + '\n' + str(pwd)

    # construct WEIBO RSA Publickey using n and e above, note that n is a hex string
    key = rsa.PublicKey(int(weibo_rsa_n, 16), weibo_rsa_e)

    # get encrypted password
    encropy_pwd = rsa.encrypt(message, key)
    # trun back encrypted password binaries to hex string
    return binascii.b2a_hex(encropy_pwd)


def get_user(username):
    username_ = urllib2.quote(username)
    username = base64.encodestring(username_)[:-1]
    return username


def random_number(randomlength=8):
    rn = ''
    for i in range(0, randomlength):
        rn += str(random.randint(0, 9))
    return rn

def auto_decode(data):
    encoding = chardet.detect(data)['encoding']
    print('encoding', encoding)
    if encoding not in ['ascii', None]:
        data = data.decode(encoding)
    return data