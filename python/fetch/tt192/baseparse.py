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
baseurl = "https://www.192tt.com"
channel = 'self_192tt_more'
header = {'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl,
          'cookie':"UM_distinctid=1684d7cba67f5-022d48a4e4ab25-47e1039-1fa400-1684d7cba68d79; CNZZDATA1271287856=37792403-1547484196-%7C1547484196; vihwnecookieclassrecord=%2C34%2C; Hm_lvt_2ef72d742c2dcbcc370f30349d903e91=1547488247; Hm_lpvt_2ef72d742c2dcbcc370f30349d903e91=1547488247"}
maxPage = 50
maxCount = 3
regVideo = re.compile(r'{ type: "application/x-mpegurl", src:"(.*)" }')
channel_more = ['https://www.192tt.com/meitu/',
                'https://www.192tt.com/gc/', 'https://www.192tt.com/gq/']
# channel_more = [ 'http://www.192tt.com/gq/']


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
