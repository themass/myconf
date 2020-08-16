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
baseurl = "https://www.tianjiyy123.com/"
header={'Cookie':"PHPSESSID=a64ehbafjhsprpvaafaqtv1613; Hm_lvt_e0cbf7df84e2fd29f16d2fe750460260=1597414959; Hm_lvt_4f0357970c786756d2eac01267e7a035=1597414959; Hm_lpvt_4f0357970c786756d2eac01267e7a035=1597549834; Hm_lpvt_e0cbf7df84e2fd29f16d2fe750460260=1597549834",
                'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13', "Referer":baseurl}
maxCount = 3
regVideo = re.compile(r"http(.*?)m3u8")
videoApiMp4 = re.compile(r'http(.*?)\.mp4')

shareVideo = re.compile(r"http(.*?)/share/(.*?)")

class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def fetchUrl(self, url, aheader={}):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(baseurl + url,headers=header)
                req.encoding = 'utf-8'
                response = urllib2.urlopen(req, timeout=300)
                content = response.read().decode('utf8', errors='replace')
                soup = BeautifulSoup(content)
                return soup
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', baseurl + url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', url
        return BeautifulSoup('')

    def fetchUrlWithBase(self, url, aheader={}):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(url,headers=header)
                req.encoding = 'utf-8'
                response = urllib2.urlopen(req, timeout=300)
                content = response.read().decode('utf8', errors='replace')
                soup = BeautifulSoup(content)
                return soup
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', url
        return BeautifulSoup('')

    def fetchContentUrlWithBase(self, url, aheader={}):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(url,headers=header)
                req.encoding = 'utf-8'
                response = urllib2.urlopen(req, timeout=300)
                content = response.read().decode('utf8', errors='replace')
                return content
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', baseurl+url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', baseurl+url
        return ''

    