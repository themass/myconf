#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import urllib2
import threading
from common.envmod import *
from common import db_ops
from common import common
import threading
from BeautifulSoup import BeautifulSoup
import re
# http://www.dehyc.com
baseurl = "http://www.192tt.com"
channel = 'self_192tt_more'
header = {'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl}
maxPage = 50
maxCount = 3
regVideo = re.compile(r'{ type: "application/x-mpegurl", src:"(.*)" }')
# channel_more = ['http://www.192tt.com/meitu/',
#                 'http://www.192tt.com/gc', 'http://www.192tt.com/gq/']
channel_more = [ 'http://www.192tt.com/gq/']


class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

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
                print '打开页面错误,重试',  url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', url
        return BeautifulSoup('')
