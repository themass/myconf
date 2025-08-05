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
import sys
reload(sys)
sys.setdefaultencoding('utf8')
# http://www.dehyc.com
channels = ['/vod/listing-0-0-0-0-0-0-0-0-0-']
baseurl = "https://wtsw28ah5a8q75g07ywb.lagoapps.com"
header = {'Cookie':'UM_distinctid=172f618d129281-055f55fad65761-47e1039-100200-172f618d12c2fb; ASPSESSIONIDCGTBTCBS=PMKJAEJDCEIHOGLMBCBGIGIA; ASPSESSIONIDCGQDTBDT=BGBOJDKDFAEGAAILGPKJOHOA; MAX_HISTORY={video:[{"name":"\u673A\u5173\u67AA\u56DA\u5F92","link":"http://www.tlyy.cc/dy/dy1/jiguanqiangqiutu/","pic":"https://pic.kssxdd.com/uploadimg/2020-6/20206249343540317.jpg"},{"name":"\u5E08\u7236","link":"http://www.tlyy.cc/dy/dy1/shifu/","pic":"https://pic.kssxdd.com/uploadimg/2015-12/201512140295682712.jpg"}]}; CNZZDATA4664080=cnzz_eid%3D1805056799-1593266144-https%253A%252F%252Fwww.baidu.com%252F%26ntime%3D1593271544; ASPSESSIONIDAERDRBDS=EMCIHLKDNJLPGOMGOJBGOHLF; ASPSESSIONIDAESDRADS=BGDFMLJDMFPAJIJOKKICJKFM; cscpvrich6565_fidx=3',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36', "Referer":baseurl
                ,"Host": "wtsw28ah5a8q75g07ywb.lagoapps.com","Accept-Encoding": "gzip"}
maxCount = 3
videoApi = re.compile(r'http(.*?)\.m3u8')
videoApiMp4 = re.compile(r'http(.*?)\.mp4')

shareVideo = re.compile(r"http(.*?)/share/(.*?)")

videoId = re.compile("/vodhtml/(.*?)\.html")
class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def fetchUrl(self, url, aheader=header):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(baseurl + url, headers=aheader)
                content = urllib2.urlopen(req, timeout=30).read()
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
                content = urllib2.urlopen(req, timeout=30).read()
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
                content = urllib2.urlopen(req, timeout=30).read()
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
        with open("kdp2/header.html") as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist
    