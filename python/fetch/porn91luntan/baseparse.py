#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import zlib
import urllib2
import threading
import os
import re
import sys
import time
from common.envmod import *
from common import db_ops
from common import common
from BeautifulSoup import BeautifulSoup
reload(sys)
sys.setdefaultencoding('utf8')

# 91自拍论坛 文字区（域名会轮换，当前 sol140）
baseurl = "https://t924.sol140.com/"
header = {
    'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Referer': baseurl,
}
maxCount = 3
regVideo = re.compile(r'http(.*?)m3u8')
namereg = re.compile(r"(&#[0-9]*;)+")


class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def _full_url(self, url):
        if not url:
            return baseurl
        if url.startswith('http'):
            return url
        return baseurl + url.lstrip('/')

    def fetchUrl(self, url):
        count = 0
        full = self._full_url(url)
        while count < maxCount:
            try:
                req = urllib2.Request(full, headers=header)
                response = urllib2.urlopen(req, timeout=60)
                content = response.read()
                if not isinstance(content, unicode):
                    content = content.decode('utf-8', 'replace')
                return BeautifulSoup(content)
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', full, '次数', count
                count = count + 1
                time.sleep(1)
        print '打开页面错误,重试3次还是错误', url
        return BeautifulSoup('')

    def fetchUrlWithBase(self, url):
        return self.fetchUrl(url)

    def header(self):
        content = ''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__))
        with open("porn91luntan/header.html") as f:
            for line in f.readlines():
                content = "%s%s" % (content, line)
        soup = BeautifulSoup(content)
        return soup.findAll('a')

    def header2(self):
        content = ''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__))
        with open("porn91luntan/header2.html") as f:
            for line in f.readlines():
                content = "%s%s" % (content, line)
        soup = BeautifulSoup(content)
        return soup.findAll('a')

    def fetchContentUrlWithBase(self, url):
        count = 0
        full = self._full_url(url)
        while count < maxCount:
            try:
                req = urllib2.Request(full, headers=header)
                return urllib2.urlopen(req, timeout=60).read()
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', full, '次数', count
                count = count + 1
                time.sleep(1)
        print '打开页面错误,重试3次还是错误', url
        return ''
