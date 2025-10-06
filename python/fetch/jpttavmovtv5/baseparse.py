#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import zlib
import time
import urllib2
import threading
from common.envmod import *
from common import db_ops
from common import common
import threading,os
from BeautifulSoup import BeautifulSoup
import re,sys
reload(sys)
# 
sys.setdefaultencoding('utf8')

# 9226688.com 8182277.com 8283377.com qqav10.com qqav9.com qqav8.com qqav7.com qqav6.com qqav5.com 
baseurl = "https://jpttavmovtv5.cc"
header = {'User-Agent':
          'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html）Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)', 
          'Cookie':'_ga=GA1.1.84703687.1759636500; _clck=1emkx0z%5E2%5Efzw%5E0%5E2104; UGVyc2lzdFN0b3JhZ2U=%7B%7D; __PPU_cl_tl=zQIAgqFs0mjh7CyhYwE; __PPU_puid=7372220048289729256; __PPU_ppucnt=3; XSRF-TOKEN=eyJpdiI6IkFMMzZCUjNpKzBORElXVDhwQzJUUVE9PSIsInZhbHVlIjoiNUx5N1Z5Ri9LSUxyVlhTSkFuemd6K0c5dTBDa1I4QzJMZXRoV0s1L29wYzA3cit3d3JPVDRDbUJ5OXRDNHpKRFZSQSs2MnFGM05RbVVRKzQ4Z1FHOVAvUXZZeEtFTFdyOVFoQWRNcUN2MW1VZ2lUU2F0VlNWTWEwWVZpdDdxZHAiLCJtYWMiOiJkNzA2YmUzYWZiOWNjY2FkZmYyMzhjNjdmN2E2Njc2YWM0ZTMyNGNiNzg5ZmViNTQ0MTQ1MWI4MGJiMTZmZGU4IiwidGFnIjoiIn0%3D; jptt_session=eyJpdiI6IjhIdGVkWENJQ3BxVW4rWmRhL1N2VVE9PSIsInZhbHVlIjoia3BSU21aTnBoa2ZMeVE3ZTN3Lzl0dlZUek5nSmU5WDhiZkFtQWxoa2tmZTdlZEVTS3A4bG50TCtVSXdWMVVWajhrWUlCOHpPWXRWdkRpVndNMUV5ZnNLbjVreGV3a3dhSUZvUFcxMXd1RkhTS1Q5NjFNL2hSeXZlUWRWazJDYmMiLCJtYWMiOiJlZGZkNjljNjMwZjA0Yzg2NDNmMmIwMDljMzZiNDZjZTg2OWQxOGE3ZDA0OWZkODBmMWQxOWEwNjBlNmRhYTliIiwidGFnIjoiIn0%3D; _ga_TCQW0Y1FZ8=GS2.1.s1759636500$o1$g1$t1759638268$j60$l0$h0; _clsk=pp7xli%5E1759638271842%5E17%5E0%5En.clarity.ms%2Fcollect'
          ,"Referer": baseurl}
maxCount = 3
regVideo = re.compile(r'http(.*?)m3u8"')
namereg = re.compile(r"(&#[0-9]*;)+")

class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def fetchUrl(self, url):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(baseurl + url, headers=header)
                req.encoding = 'utf-8'
                response = urllib2.urlopen(req, timeout=3000)
                gzipped = response.headers.get(
                    'Content-Encoding')  # 查看是否服务器是否支持gzip
                content = response.read().decode('utf-8', errors='replace')
                if gzipped:
                    content = zlib.decompress(
                        content, 16 + zlib.MAX_WBITS)  # 解压缩，得到网页源码
                soup = BeautifulSoup(content)
                return soup
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', baseurl + url, '次数', count
                count = count + 1
                time.sleep(1)

        print '打开页面错误,重试3次还是错误', url
        return BeautifulSoup('')

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
                time.sleep(1)

        print '打开页面错误,重试3次还是错误', url
        return BeautifulSoup('')
    def header(self):
#         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__)) 
        with open("jpttavmovtv5/header.html") as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        print content
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist
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
                time.sleep(1)

        print '打开页面错误,重试3次还是错误', url
        return ''

    