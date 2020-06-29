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
channels = ['/vod/listing-0-0-0-0-0-0-0-0-0-']
baseurl = "https://wtsw28ah5a8q75g07ywb.lagoapps.com"
header = {'token':
          'bmFXcHBmemI0RzdJaVh5ZzlQOHNiZUh3L0FYa1pldzRoTmRScnByanN4bWllUURzUzJZTUx3VXprWlZ4QXhVV0ZuVUJmNGlXSkZORHN6RmNZMmNqRmJ1WFhCVk04VlE2d25ZcnJhRXdxN0tENUNWYjd3dnZ3eGgzNnFmS0pDUnk=', "Referer": baseurl
          ,"User-Agent": "okhttp/3.10.0","Host": "wtsw28ah5a8q75g07ywb.lagoapps.com","Accept-Encoding": "gzip"

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
    