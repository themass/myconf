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
import os
baseurl = "https://cn.jav101.com"
header = {'Cookie':'__cfduid=dd4573f23e457274464ab236132a125081548501565; locale=cn; _ga=GA1.2.82358204.1548501415; _gid=GA1.2.1826257584.1548501415; XSRF-TOKEN=eyJpdiI6InR4NEVWZXAybXErSkVyQ3NcL1dtWlR3PT0iLCJ2YWx1ZSI6IkdNaXF0Q20xTWJzWTFzeTZaZXlGeFdnNEdvTXY0d2o1alwvU2dKZXo5SVV2eHNIOGptWTFcL09tTGlUdEp0enlIQSIsIm1hYyI6ImI2ODYzYzE1MTJiZWZjMjgxZjJiZGNjMTg4NjU5OTM4YmExNzlhNDExMzFjZDRkMmU0ZDNmZDQ2ODllZTYwNDcifQ%3D%3D; jav101_sessions=eyJpdiI6IjFJKzViZ3NxQ1dHRjBLVzlnbkNwdFE9PSIsInZhbHVlIjoibWF5K0ZpOXVOZVhka2dGRXFQQWtIQXU1am1od05HNWlqY1QzbVpTXC9qSHNkcGduXC9Ec3JvRFNEZjZWRVVcL1ZXVyIsIm1hYyI6IjMzNjhmZTQyNzk0MGNkNzc0NzAwNDY2MTVjNDU0MTY2M2Q1NWQ5YWZiYjQzOWEwOWY2Y2U4ZjVjMDdmNzg1YTgifQ%3D%3D; _gat_UA-51244524-6=1; _gat_UA-51244524-1=1','User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl}
maxCount = 3
regVideo = re.compile(r"http(.*?)m3u8")
regVideo2 = re.compile(r"mac_url=unescape\('(.*?)'\);")

class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def fetchUrl(self, url, aheader=header):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(baseurl + url, headers=aheader)
                req.encoding = 'utf-8'
                response = urllib2.urlopen(req, timeout=300)
                gzipped = response.headers.get(
                    'Content-Encoding')  # 查看是否服务器是否支持gzip
                content = response.read().decode('utf8', errors='replace')
                if gzipped:
                    content = zlib.decompress(
                        content, -zlib.MAX_WBITS)  # 解压缩，得到网页源码
                soup = BeautifulSoup(content)
                return soup
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', baseurl + url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', url
        return BeautifulSoup('')
    def header(self):
#         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__)) 
        with open("lusibi/header.html") as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist
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

    def fetchContentUrl(self, url, aheader=header):
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

    