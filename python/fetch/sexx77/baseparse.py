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
# http://www.dehyc.com
baseurl = "http://www.segui1.xyz/"
videolUrl='/stli_gthdrdbn/29.html'
header = {'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl}
maxCount = 3
videoApi = re.compile(r'var redirecturl = "(.*)";')
videoApim3 = re.compile(r'var main = "(.*)";')

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
    def header(self,name):
        soup = self.fetchUrl("", header)
        objs =[]
        uls = soup.findAll('ul',{'class':'nav_menu clearfix'})
        for ul in uls:
            active = ul.first("li",{'class':'active'})
            if active.text==name:
                alist = ul.findAll('a')
                for ahref in alist:
                    obj ={}
                    obj['name']=ahref.text
                    obj['url']=ahref.get('href')
                    objs.append(obj)
        return objs
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

        print '打开页面错误,重试3次还是错误', url
        return BeautifulSoup('')

    def fetchContentUrlWithBase(self, url):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(url, headers=header)
                content = urllib2.urlopen(req, timeout=300).read()
                return content
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', url
        return ''

    