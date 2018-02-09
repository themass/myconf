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
baseurl = "http://yezmw.com"
channel_pre = 'self_yezmw_'
header = {'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": "http://yezmw.com"}
maxCount = 3
regVideo = re.compile(r'{ type: "application/x-mpegurl", src:"(.*)" }')


class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def fetchUrl(self, url, aheader=header):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(baseurl + url, headers=aheader)
                content = urllib2.urlopen(req, timeout=300).read()
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
                content = urllib2.urlopen(req, timeout=300).read()
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
                content = urllib2.urlopen(req, timeout=300).read()
                return content
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', url
        return ''

    def fetchHeadChannel(self):
        try:
            soup = self.fetchUrl("/")
            menu = soup.first("ol", {"class": "block"})
            if menu == None:
                print '没找到对应的频道 ', baseurl
                return None
            lis = menu.findAll("li")
            ret = []
            start = False
            for li in lis:
                a = li.first('a')
                print a
                if a != None and a.text.find('首页') == -1:
                    if a.text=='制服中文av':
                        start=True
                    if start==True:
                        row = {}
                        row['name'] = a.text
                        row['baseurl'] = baseurl
                        row['url'] = a.get('href')
                        row['channelType'] = 'normal'
                        row['updateTime'] = datetime.datetime.now()
                        row['channel'] = baseurl.replace("http://", "").replace("https://", "")+channel_pre + a.get('href')
                        ret.append(row)
            return ret
        except Exception as e:
            print common.format_exception(e)
