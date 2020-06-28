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
baseurl = "https://8guj.com"
header = {'cookie':
          'visid_incap_198246=/Lxvc98LRdGQWKCwYpQepQCOYVwAAAAAQUIPAAAAAACdUJ4LVw6sd5fRL+WAeJ9X; Hm_lvt_3fc5d297baf7a22b3182ef87040c41aa=1549897219; visid_incap_1860115=//BuYAg2RQGvtKj/tKH4LgKOYVwAAAAAQUIPAAAAAADE5SfgREXnpKddKsOaYqt7; mac_history=%7Bvideo%3A%5B%7B%22name%22%3A%22%u4F20%u5947%22%2C%22link%22%3A%22/vod-detail-id-56774.html%22%2C%22typename%22%3A%22%u6218%u4E89%u7247%22%2C%22typelink%22%3A%22/vod-type-id--pg-1.html%22%2C%22pic%22%3A%22upload/vod/2018-02-12/151842606318.jpg%22%7D%2C%7B%22name%22%3A%22%u75AF%u72C2%u7684%u5916%u661F%u4EBA%22%2C%22link%22%3A%22/vod-detail-id-96281.html%22%2C%22typename%22%3A%22%u52A8%u4F5C%u7247%22%2C%22typelink%22%3A%22/vod-type-id--pg-1.html%22%2C%22pic%22%3A%22upload/vod/2018-03-21/15216193053.jpg%22%7D%2C%7B%22name%22%3A%22%u6D41%u6D6A%u5730%u7403%22%2C%22link%22%3A%22/vod-detail-id-96391.html%22%2C%22typename%22%3A%22%u52A8%u4F5C%u7247%22%2C%22typelink%22%3A%22/vod-type-id--pg-1.html%22%2C%22pic%22%3A%22upload/vod/2018-03-21/152161944111.jpg%22%7D%2C%7B%22name%22%3A%22%u6C99%u6F20%u9A7C%u5F71%22%2C%22link%22%3A%22/vod-detail-id-4858.html%22%2C%22typename%22%3A%22%u7EAA%u5F55%u7247%22%2C%22typelink%22%3A%22/vod-type-id--pg-1.html%22%2C%22pic%22%3A%22/template/zssy/images/load.gif/vod/2017-04-29/201704291493454705.jpg%23err2018-09-16%22%7D%5D%7D', "Referer": baseurl
          ,"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
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
        with open("bx88222/header.html") as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist
    