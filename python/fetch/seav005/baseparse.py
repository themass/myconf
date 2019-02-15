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
baseurl = "http://www.seav005.com/"
header = {'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl,
          "Cookie":"QKDa_2132_saltkey=lp7hMhMv; QKDa_2132_lastvisit=1550250023; UM_distinctid=168f2467f00317-064390b448af1f-47e1039-1fa400-168f2467f023d2; QKDa_2132_atarget=1; QKDa_2132_cmid=2058295; QKDa_2132_sendmail=1; QKDa_2132_seccode=2032.51fffbc746f03e3d6f; QKDa_2132_ulastactivity=69797Bhsq7UkOhdAuw3w0HEkvOPvh3yJE6v9zKYBsMK6%2BaRMalSS; QKDa_2132_auth=65317c9D%2BkZmuxJr2glM0Y8OQbYiXdwSn3DsdFIACXRkE80Hy5uHVkL8ghNhkdLRtw%2BcOo718BjFv%2BHjbCIVGm3gXPi9; QKDa_2132_security_cookiereport=6fa0gLyzO4NGDXn%2BJzSUOLNYcFmcTdx73cnDM8SMQPxzMhaxIq8N; QKDa_2132_st_p=2818003%7C1550255806%7Cdccfeb2d865912106f8e65248488132b; QKDa_2132_viewid=tid_7193423; QKDa_2132_noticeTitle=1; QKDa_2132_sid=ZDi8H0; QKDa_2132_lip=47.88.7.156%2C1550255802; QKDa_2132_st_t=2818003%7C1550255837%7C4c435c98115e63b88bde20940b63243e; QKDa_2132_forum_lastvisit=D_62_1550253727D_49_1550254850D_58_1550254931D_37_1550255176D_59_1550255837; QKDa_2132_visitedfid=59D2D37D58D49D62; CNZZDATA1260462880=889112913-1550248139-%7C1550253540; CNZZDATA1260178197=1119087455-1550249083-%7C1550254091; QKDa_2132_lastact=1550255841%09misc.php%09patch"}
maxCount = 3
playVideo = re.compile(r"http(.*?)mp4")
urlMap = {"mp4":"https://p.eeoai.com","mp42":"https://p.672sp.com","jav":"http://p.164d.com"}

class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def fetchUrl(self, url, aheader=header):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(baseurl + url, headers=header)
                req.encoding = 'utf-8'
                response = urllib2.urlopen(req, timeout=300)
                gzipped = response.headers.get(
                    'Content-Encoding')  # 查看是否服务器是否支持gzip
                content = response.read().decode('GBK', errors='replace').replace("<![endif]-->","").replace("<!--[if lt IE 9]>", "").replace("<![endif]-->", "").replace("<!--","").replace(" -->","")
                m = re.findall("<!--(.*?)-->",content)
                if m!=None:
                    for i in m:
                        content = content.replace(i,"")
                content = content.replace("<!---->","")
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
    def header(self):
#         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__)) 
        with open("seav005/header.html") as f:
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

    