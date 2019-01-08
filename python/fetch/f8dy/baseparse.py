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
import re,os
# http://www.dehyc.com
baseurl = "https://www.f8dy.tv"
header = {'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl,
          "cookie":"UM_distinctid=167986dd69fe4-07c07e383f6953-47e1039-1fa400-167986dd6a224b; __cm_warden_upi=MjIxLjIxNi4xMzYuMTMx; PHPSESSID=r4j316961t789re32hrottv74h; Hm_lvt_430320e5a506b3c18788616c9beb93b7=1544450594,1546960402; 2401_2223_221.216.136.131=1; CNZZDATA1274765652=1549884782-1544450563-%7C1546959788; __cm_warden_uid=80b2b37fa34a861ec726975d26a5e56dcookie; is_show_dsn=1; UBGLAI63GV=HHQKB.1546960994; Hm_lpvt_430320e5a506b3c18788616c9beb93b7=1546960995; CNZZDATA1275441972=774796427-1546959438-https%253A%252F%252Fwww.f8dy.tv%252F%7C1546959438; iiad_img_has_show_885=4497%7C325%2C3813%7C718%2C4430%7C720%2C4538%7C325%2C4429%7C719; _s_v_1510=325%2C718%2C720%2C719%2C"}
maxCount = 3
videoApi = re.compile(r'http(.*?)\.m3u8')
videoId = re.compile("/vodhtml/(.*?)\.html")
class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def fetchUrl(self, url, aheader=header):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(baseurl + url, headers=aheader)
                content = urllib2.urlopen(req, timeout=5000).read()
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
                req = urllib2.Request(url, headers=aheader)
                content = urllib2.urlopen(req, timeout=300).read()
                return content
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', url
        return ''
    def header(self):
#         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__)) 
        with open("f8dy/header.html") as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist
    