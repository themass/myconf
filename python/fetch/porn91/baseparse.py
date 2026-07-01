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
baseurl = "https://rfd0i4.jstv800.com"
header = {'User-Agent':
          'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html）Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)', 
          'Cookie':'_ym_uid=1726938050509318806; _ga=GA1.1.1936408816.1742034872; _ym_d=1774863920; server_name_session=e9ab65b41bb7d5b3bc4b9d8fbb495d8b; _ym_isad=2; _ym_visorc=b; _ga_F8MXJQGLN1=GS2.1.s1778856727$o11$g1$t1778856807$j60$l0$h1105965748; cf_clearance=5Lkp8o9jlg3swV4pmFI1.Tm94S5A_eFhCx9P_qZV89M-1778856807-1.2.1.1-iH8GS2VMEzkGhkARZmhyqBejH6G2CwJFOxtUKMSAbeyzbomX_N3tu7yvNIrdJat.d6mz17mfZ.3oZiyimFIP8.iYnBhz0Qs6dAuXmOkbLyi.rRmO0kUhxiIB6gSJtDR0l4faFJTtsFISJCzygk6UbZOiz9SwmpKspoNIoDpZbjsUZNOfwzwFttek2nTCbdspME_2kpfB5W9xOyDneQkwEzMGO0hKXYBSgk1yLLQFoQA0nK_TMeETiEqwKfrwiu2FfbUJmfNflenTxgnwRJ3czZSneygZdzlw17Blgdf03WYSFiEHZNLvkVCajHcRZwdHnD72odxdcbTunHcTEWaAWw'
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
        with open("porn91/header.html") as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        print content
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist
    def header2(self):
        #         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__))
        with open("porn91/header2.html") as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        print content
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist
    def fetchContent(self, url):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(baseurl+url, headers=header)
                content = urllib2.urlopen(req, timeout=300).read()
                return content
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', url, '次数', count
                count = count + 1
                time.sleep(1)

        print '打开页面错误,重试3次还是错误', url
        return ''

    