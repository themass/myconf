#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import json
import zlib
import time
import urllib2
import threading
import os
import re
import sys
from common.envmod import *
from common import db_ops
from common import common
from BeautifulSoup import BeautifulSoup
reload(sys)
sys.setdefaultencoding('utf8')

baseurl = "https://ddys.io/"
apiBase = "https://ddys.io/api/v1"
header = {
    'User-Agent':
        'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html）Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'Accept': 'application/json,text/html,*/*',
    'Referer': baseurl,
}
maxCount = 3
regVideo = re.compile(r'http(.*?)m3u8"')
namereg = re.compile(r"(&#[0-9]*;)+")
perPage = 24


class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def fetchUrl(self, url):
        count = 0
        while count < maxCount:
            try:
                full = url if url.startswith('http') else (baseurl + url.lstrip('/'))
                req = urllib2.Request(full, headers=header)
                response = urllib2.urlopen(req, timeout=300)
                gzipped = response.headers.get('Content-Encoding')
                content = response.read().decode('utf-8', errors='replace')
                if gzipped:
                    content = zlib.decompress(content, 16 + zlib.MAX_WBITS)
                return BeautifulSoup(content)
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', url, '次数', count
                count = count + 1
                time.sleep(1)
        print '打开页面错误,重试3次还是错误', url
        return BeautifulSoup('')

    def fetchUrlWithBase(self, url):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(url, headers=header)
                content = urllib2.urlopen(req, timeout=300).read()
                return BeautifulSoup(content)
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', url, '次数', count
                count = count + 1
                time.sleep(1)
        print '打开页面错误,重试3次还是错误', url
        return BeautifulSoup('')

    def fetchJson(self, url):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(url, headers=header)
                response = urllib2.urlopen(req, timeout=300)
                content = response.read()
                if not isinstance(content, unicode):
                    content = content.decode('utf-8', 'replace')
                return json.loads(content)
            except Exception as e:
                print common.format_exception(e)
                print '打开API错误,重试', url, '次数', count
                count = count + 1
                time.sleep(1)
        print '打开API错误,重试3次还是错误', url
        return None

    def header(self):
        content = ''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__))
        with open("ddys/header.html") as f:
            for line in f.readlines():
                content = "%s%s" % (content, line)
        soup = BeautifulSoup(content)
        return soup.findAll('a')
