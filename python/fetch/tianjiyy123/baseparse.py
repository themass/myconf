#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import zlib
import urllib2
import threading
from common.envmod import *
from common import db_ops
from common import common
import threading
from BeautifulSoup import BeautifulSoup
import re
# http://www.dehyc.com
baseurl = "http://www.tianjiyy123.com"
header = {'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl}
maxCount = 3
regVideo = re.compile(r"http(.*)m3u8")


class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def fetchUrl(self, url, aheader=header):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(baseurl + url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13', "Referer":baseurl})
                req.encoding = 'utf-8'
                response = urllib2.urlopen(req, timeout=300)
                gzipped = response.headers.get(
                    'Content-Encoding')  # 查看是否服务器是否支持gzip
                content = response.read()
                if gzipped:
                    content = zlib.decompress(
                        content, 16 + zlib.MAX_WBITS)  # 解压缩，得到网页源码
                soup = BeautifulSoup(content)
                return soup
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', baseurl + url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', url
        return BeautifulSoup('')

    def fetchUrlWithBase(self, url, aheader=header):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(url, headers=aheader)
                content = urllib2.urlopen(req, timeout=300).read()
                soup = BeautifulSoup(content)
                return soup
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', url
        return BeautifulSoup('')

    def fetchContentUrlWithBase(self, url, aheader=header):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(baseurl+url, headers=aheader)
                content = urllib2.urlopen(req, timeout=300).read()
                return content
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', baseurl+url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', baseurl+url
        return ''

    