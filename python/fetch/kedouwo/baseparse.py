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
baseurl = "http://www.aotu48.com"
baseurl2= "https://www.v88hd.space/"
baseurl3= "http://asy007.com/"
header = {'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl,
          'Cookie':"ASPro_3b178725fc4f483c1b3b540e9254fe69=rjglqktt458s6t79lurudu6u37; __51cke__=; __atuvc=5%7C34; __atuvs=5b7d8978e2390365001; __tins__19260318=%7B%22sid%22%3A%201534952887546%2C%20%22vd%22%3A%2012%2C%20%22expires%22%3A%201534956279466%7D; __tins__18963094=%7B%22sid%22%3A%201534952887602%2C%20%22vd%22%3A%2012%2C%20%22expires%22%3A%201534956279478%7D; __51laig__=27"}
header2 = {'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl,
          'Cookie':"pxTK_2132_saltkey=CDKD7k08; pxTK_2132_lastvisit=1534866582; _ga=GA1.2.676201030.1534870386; _gid=GA1.2.1608862136.1534870386; Hm_lvt_a7f417c344bdcfebc00a1b4084b35417=1534870386,1534952916; pxTK_2132_sid=mFy09c; pxTK_2132_st_p=0%7C1534955323%7C896e471f57aa95da32adf071ecf4097b; pxTK_2132_viewid=tid_11237; pxTK_2132_st_t=0%7C1534955633%7C29fb8f0eb614b2081f3c458d979f7266; pxTK_2132_forum_lastvisit=D_45_1534955312D_38_1534955633; pxTK_2132_visitedfid=38D45; Hm_lpvt_a7f417c344bdcfebc00a1b4084b35417=1534955838; _gat_gtag_UA_118038554_1=1; pxTK_2132_lastact=1534955633%09home.php%09misc; pxTK_2132_sendmail=1"}
header3 = {'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl,
          'Cookie':"PHPSESSID=14uflkff1ehg7lk7sjifkbm1l2; Hm_lvt_3ba47f3a5faa80b14ec0eaededbe6d3c=1534871240,1534957616; Hm_lpvt_3ba47f3a5faa80b14ec0eaededbe6d3c=1534957632"}
maxCount = 3
maxCount = 3
regVideo = re.compile(r"src=\"(.*?)\"frameborder")
regVideoM3 = re.compile(r"http(.*?)m3u8")

class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def header(self):
#         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__)) 
        with open("kedouwo/header.html") as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist
    def header2(self):
#         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__)) 
        with open("kedouwo/header2.html") as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist
    def header3(self):
#         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__)) 
        with open("kedouwo/header3.html") as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist
    def fetchUrl(self, url, aheader=header):
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
                req = urllib2.Request(url, headers=aheader)
                content = urllib2.urlopen(req, timeout=300).read()
                return content
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', url
        return ''

    