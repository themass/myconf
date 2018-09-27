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
header = {'Cookie':'__cfduid=dfb17827112b8fe2e45c467a5bc61015e1538060863; rr=direct; iadult=1; hello=1; _ga=GA1.2.384091810.1538060865; _gid=GA1.2.251488469.1538060865; _gat_gtag_UA_78207029_1=1; XSRF-TOKEN=eyJpdiI6InZpMDJ1WmtRTXhUbnRPNHFxYzNuNXc9PSIsInZhbHVlIjoiTGFYZDBYckhwTE1yR3hIZ0d4bXhsck1FS0ZKY1NWVVpIRm5GM085Tmp3SDJZbVptRGhaQ0N3a08rYlIzYXl0NEM3ZGlEcVI2UXBqTThqRUFvTmsxRVE9PSIsIm1hYyI6IjVkMGI0MjNiMjI5ZGMzYzkyNWU1YzY3ZDdkNzhjYzY2YTA1MzBiNzNkMWVjMDNlNjE5Mzg0ZjdlNmMxZmM1YWQifQ%3D%3D; miao_ss=eyJpdiI6InR1VmRUMHRmUWJrYnF4bDBkd3RlV0E9PSIsInZhbHVlIjoieFBiUmJGeWJOZ1A1a1pKVTJZWUtnVkt0ZHNiUmUwZmhvTE1LN2MyRkZCQXNidWh2S3JMMzNYRFh2VittR3FcL3crMjJub0JPNUtJdExMUFJ5V1ZtWXRRPT0iLCJtYWMiOiIwY2IxZTI5YzhkOGJjMjMwMDUwZTkzNzFjOTY0MDk4NzNhNDliNzJkZmE5MzM3YzE5ZTFiMzRiZTMyYWE5ZmQ4In0%3D','User-Agent':
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

    