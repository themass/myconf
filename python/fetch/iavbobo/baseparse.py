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
import sys,json
reload(sys)
sys.setdefaultencoding('utf8')
# http://www.dehyc.com
baseurl = "http://api.iavbobo.com"
aheader = {'Cookie':"__cfduid=d32f5facd223cb71c985dcbb27b8de01e1529461416",
                'User-Agent': 'okhttp/3.6.0', "Referer":baseurl,
                "authorization":"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJtYW4iOiJIVUFXRUkiLCJicmFuZCI6IkhVQVdFSSIsInN5c3RlbU5hbWUiOiJBbmRyb2lkIiwic3lzdGVtVmVyc2lvbiI6IjguMC4wIiwidW5pcXVlIjoiNzE5MmM5M2RhNzYxZDQyYSIsImlhdCI6MTUyOTQ2MTQzNiwiZXhwIjoxNTI5NDk3NDM2fQ.RK81muRt9HfLw5l6erM12rbfDNBFnwOqa-zEuSL7zHw"}
maxCount = 3
regVideo = re.compile(r"http(.*)m3u8")
regVideoYun = "/share/"

class BaseParse(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)

    def fetchUrl(self, url):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(baseurl+url, headers=aheader)
                content = urllib2.urlopen(req, timeout=300).read()
                return json.loads(content)
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', baseurl + url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', url
        return {}

