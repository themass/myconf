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
baseurl = "http://www.gc183.com"
maxCount = 5
video_iframe = re.compile("vod-detail-id-(.*?)/.html")
video_url ="/?m=vod-play-id-%s-src-1-num-1.html"
regVideo = re.compile(r"http(.*?)m3u8'")

class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def fetchUrl(self, url):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(baseurl + url, headers={"cookie":"__cfduid=d58c3185a110d78073b2c5f00f7e441721528213141; PHPSESSID=6qsp96alribdf09kch8beg25p1; _ga=GA1.2.1055870002.1528213149; _gid=GA1.2.222912981.1528213149; _gat_gtag_UA_117149527_1=1",'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13', "Referer": baseurl})
                req.encoding = 'utf-8'
                response = urllib2.urlopen(req, timeout=300)
                gzipped = response.headers.get(
                    'Content-Encoding')  # 查看是否服务器是否支持gzip
                content = response.read()
                contentstr = content
                if gzipped:
                    fio = StringIO.StringIO(content)
                    f = gzip.GzipFile(fileobj=fio)
                    contentstr = f.read()
                    f.close()
                soup = BeautifulSoup(contentstr)
                return soup
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', baseurl + url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', baseurl + url
        return BeautifulSoup('')

    def fetchHead(self, name):
        try:
            soup = self.fetchUrl('/')
            menus = soup.findAll("div", {"class": "caoporn_nav"})
            for menu in menus:
                active = menu.first("a", {'class':"caoporn_nav_l"}).text
                print active
                if active.count(name) > 0:
                    return menu.first('ul',{'class':"caoporn_nav_r"}).findAll('a')
        except Exception as e:
            print common.format_exception(e)

