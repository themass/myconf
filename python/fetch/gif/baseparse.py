#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import urllib2
import threading
from BeautifulSoup import BeautifulSoup
from common import common
from common import MyQueue
from common.envmod import *
from common import db_ops
import re
import gzip
import StringIO
import sys
reload(sys)
sys.setdefaultencoding('utf8')
baseurl1 = "http://www.wowant.com/xieegif/"
baseurl2 = "http://www.hugao8.com/category/gao-gif/"
baseurl3 = "http://www.ratoo.net/a/gif/list_47_1.html"
baseurl4 = "http://www.neihanpa.com/gif/"
maxCount = 5
class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def fetchUrl(self, url):
        count = 0
        while count < maxCount:
            try:
                header = {'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": url}
                req = urllib2.Request(url, headers=header)
                content = urllib2.urlopen(req, timeout=3000).read()
                soup = BeautifulSoup(str(content))
                return soup
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', url
        return BeautifulSoup('')
