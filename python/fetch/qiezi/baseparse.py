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
channels = '''
{
        "mytags": [
            {
                "id": 10055,
                "name": "野外"
            },
            {
                "id": 10058,
                "name": "厨房"
            },
            {
                "id": 10302,
                "name": "酒店"
            },
            {
                "id": 10307,
                "name": "泳池"
            },
            {
                "id": 10163,
                "name": "口交"
            }
            {
                "id": 10144,
                "name": "巨乳"
            },
            {
                "id": 10141,
                "name": "制服"
            },
            {
                "id": 10067,
                "name": "角色扮演"
            },
            {
                "id": 10037,
                "name": "强奸"
            },
            {
                "id": 10174,
                "name": "颜面骑乘"
            },
            {
                "id": 10210,
                "name": "SM"
            },
            {
                "id": 10293,
                "name": "人妻/少妇"
            },
            {
                "id": 10187,
                "name": "乳交"
            },
            {
                "id": 10291,
                "name": "长腿"
            },
            {
                "id": 10278,
                "name": "爆射"
            },
            {
                "id": 10170,
                "name": "舔阴"
            },
            {
                "id": 10169,
                "name": "吞精"
            },
            {
                "id": 10161,
                "name": "多P"
            },
            {
                "id": 10160,
                "name": "69"
            },
            {
                "id": 10070,
                "name": "女学生"
            },
            {
                "id": 10342,
                "name": "中国大陆"
            },
            {
                "id": 10343,
                "name": "中文字幕"
            },
            {
                "id": 10350,
                "name": "欧美"
            },
            {
                "id": 10340,
                "name": "无码"
            }
        ]
}
'''
baseurl = "http://www.acmite.vip"
header = {'token':
          'MTU1MzIyNDk5Mg==.eyJ1c2VyX2lkIjoyMzQyMTQ1fQ==.MzA2YWVjZjlkMDQ2NjMyZTkwMDg1YzRhNzRjNzRiZjg=', "Referer": baseurl
          ,"User-Agent": "okhttp/3.10.0"
}
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
    