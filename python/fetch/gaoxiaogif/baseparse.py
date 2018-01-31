#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import urllib2
import threading
from BeautifulSoup import BeautifulSoup
from common import common
from common import MyQueue
import re
import sys
import zlib
import os
reload(sys)
sys.setdefaultencoding('utf8')
baseurl = "http://www.gaoxiaogif.com"
maxCount =3

class SmartRedirectHandler(urllib2.HTTPRedirectHandler):

    def http_error_301(self, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_301(
            self, req, fp, code, msg, headers)
        return result

    def http_error_302(self, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_302(
            self, req, fp, code, msg, headers)
        return result


class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def fetchUrl(self, url):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(baseurl+url, headers={"Cookie": "zenid=b227c2098ac37d540e4579fb024e9ba9; __utma=62982011.325664695.1514618636.1514618636.1514618636.1; __utmc=62982011; __utmz=62982011.1514618636.1.1.utmcsr=seqing.one|utmccn=(referral)|utmcmd=referral|utmcct=/2059.html; __atuvc=7%7C52; __utmb=62982011.35.10.1514618636",
                                                    "Upgrade-Insecure-Requests": "1",
                                                    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13', "Referer": baseurl})
                req.encoding = 'gbk'
                opener = urllib2.build_opener()
                opener.add_handler(SmartRedirectHandler())
                urllib2.install_opener(opener)
                response = urllib2.urlopen(req, timeout=300)
                gzipped = response.headers.get(
                    'Content-Encoding')  # 查看是否服务器是否支持gzip
                content = response.read().decode('gbk', errors='replace')
                if gzipped:
                    content = zlib.decompress(
                        content, 16 + zlib.MAX_WBITS)  # 解压缩，得到网页源码
#                 cmd = ("wget %s" % (url))
#                 textlist = os.popen(cmd).readlines()

                soup = BeautifulSoup(content)
                return soup
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', url
        return BeautifulSoup('')
