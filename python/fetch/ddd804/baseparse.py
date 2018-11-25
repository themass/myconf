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
baseurl1 = "http://zzz761.com"
baseurl2 = "http://www.jiqingyazhou.org"
baseurl4 = "http://www.39vq.com"
baseurl5 = "http://www.5wuji.com"
maxCount = 5
class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def fetchUrl(self, baseurl,url):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(baseurl+url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13', "Referer": baseurl})
                req.encoding = 'utf-8'
                response = urllib2.urlopen(req, timeout=6000)
                gzipped = response.headers.get(
                    'Content-Encoding')  # 查看是否服务器是否支持gzip
                content = response.read().decode('UTF-8') 
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
                print '打开页面错误,重试', baseurl+url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', baseurl+url
        return BeautifulSoup('')

    def fetchddd804Head(self, baseurl,name):
        try:
            soup = self.fetchUrl(baseurl,"/")
            menus = soup.findAll("div", {"class": "menu"})
            channels=[]
            for menu in menus:
                active = menu.first("a", {'class':"a2"}).text
                if active.count(name) > 0:
                    alist = menu.findAll('a')
                    for item in alist:
                        if item.get('href')!="/":
                            obj={}
                            obj['name']=item.text
                            obj['url']=item.get('href')
                            obj['baseurl']=baseurl
                            channels.append(obj)
            return channels
        except Exception as e:
            print common.format_exception(e)

    def fetchjiqingyazhouHead(self, baseurl,name):
        try:
            soup = self.fetchUrl(baseurl,"/")
            menus = soup.findAll("ul", {"class": "nav_menu clearfix"})
            channels=[]
            for menu in menus:
                active = menu.first("li", {'class':"active"}).text
                if active.count(name) > 0:
                    alist = menu.findAll('a')
                    for item in alist:
                        if item.get('href')!="/":
                            obj={}
                            obj['name']=item.text
                            obj['url']=item.get('href')
                            obj['baseurl']=baseurl
                            channels.append(obj)
            return channels
        except Exception as e:
            print common.format_exception(e)
    def fetch3wujiHead(self, baseurl,name):
        try:
            soup = self.fetchUrl(baseurl,"/")
            menus = soup.findAll("ul", {"class": "nav_menu clearfix"})
            channels=[]
            for menu in menus:
                active = menu.first("li", {'class':"active"}).text
                if active.count(name) > 0:
                    alist = menu.findAll('a')
                    for item in alist:
                        if item.get('href')!="/":
                            obj={}
                            obj['name']=item.text
                            obj['url']=item.get('href')
                            obj['baseurl']=baseurl
                            channels.append(obj)
            return channels
        except Exception as e:
            print common.format_exception(e)
    def fetch39vqHead(self, baseurl,name):
        try:
            soup = self.fetchUrl(baseurl,"/")
            menus = soup.findAll("div", {"class": "menu"})
            channels=[]
            for menu in menus:
                active = menu.first("a", {'class':"a2"}).text
                if active.count(name) > 0:
                    alist = menu.findAll('a')
                    for item in alist:
                        if item.get('href')!="/":
                            obj={}
                            obj['name']=item.text
                            obj['url']=item.get('href')
                            obj['baseurl']=baseurl
                            channels.append(obj)
            return channels
        except Exception as e:
            print common.format_exception(e)
