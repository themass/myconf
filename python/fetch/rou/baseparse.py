#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import zlib
import urllib2
import threading
from common.envmod import *
from common import db_ops
from common import common
import threading,os
from BeautifulSoup import BeautifulSoup
import re,sys
import time
reload(sys)
# 
sys.setdefaultencoding('utf8')

# 9226688.com 8182277.com 8283377.com qqav10.com qqav9.com qqav8.com qqav7.com qqav6.com qqav5.com 
baseurl = "https://rou.video"
header = {'User-Agent':
          'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
          'Cookie':'_ga=GA1.1.411502871.1722356544; __Secure-next-auth.callback-url=https%3A%2F%2Frou.video; __Host-next-auth.csrf-token=95e56b9600e27f61c20112002971c142fa675baef7afd7bc68bfb7e82c2969b2%7C40d00143474092c600adab5f004c7e058d3f59bc098c93da9c2f7cbf364bec08; _ym_uid=1722356545410363021; _ym_d=1722356545; _ym_visorc=b; _ym_isad=1; __PPU_puid=7372220048289729256; UGVyc2lzdFN0b3JhZ2U=%7B%22CAIFRQ%22%3A%22AC2zTgAAAAAAAAABAC1XhwAAAAAAAAABACxuWgAAAAAAAAABACxuWAAAAAAAAAABACxuVwAAAAAAAAABACp7EwAAAAAAAAAFACZSQQAAAAAAAAAB%22%2C%22CAIFRT%22%3A%22AC2zTgAAAABmqcTQAC1XhwAAAABmqcTQACxuWgAAAABmqcTQACxuWAAAAABmqcTQACxuVwAAAABmqcTQACp7EwAAAABmqcTQACZSQQAAAABmqcTQ%22%2C%22MTIFRQ%22%3A%22ADqyvwAAAAAAAAAFADO5uwAAAAAAAAAB%22%2C%22MTIFRT%22%3A%22ADqyvwAAAABmqcTQADO5uwAAAABmqcTQ%22%7D; bnState_1861831={"impressions":9,"delayStarted":0}; bnState_1861830={"impressions":22,"delayStarted":0}; bnState_1860832={"impressions":21,"delayStarted":0}; _ga_JFZPSL5L8E=GS1.1.1722356543.1.1.1722357885.0.0.0'
          ,"Referer": baseurl}
maxCount = 3
regVideo = re.compile(r"http(.*?)m3u8")
namereg = re.compile(r"(&#[0-9]*;)+")

class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def fetchUrl(self, url):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(baseurl + url, headers=header)
                req.encoding = 'utf-8'
                response = urllib2.urlopen(req, timeout=3000)
                gzipped = response.headers.get(
                    'Content-Encoding')  # 查看是否服务器是否支持gzip
                content = response.read().decode('utf-8', errors='replace')
                if gzipped:
                    content = zlib.decompress(
                        content, 16 + zlib.MAX_WBITS)  # 解压缩，得到网页源码
                soup = BeautifulSoup(content)
                return soup
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', baseurl + url, '次数', count
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
                soup = BeautifulSoup(content)
                return soup
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', url, '次数', count
                count = count + 1
                time.sleep(1)

        print '打开页面错误,重试3次还是错误', url
        return BeautifulSoup('')
    def header(self):
#         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__)) 
        with open("rou/header.html") as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        print content
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist
    def fetchContentUrlWithBase(self, url):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(url, headers=header)
                content = urllib2.urlopen(req, timeout=300).read()
                return content
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', url, '次数', count
                count = count + 1
                time.sleep(1)

        print '打开页面错误,重试3次还是错误', url
        return ''

    