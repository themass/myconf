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
header = {'Cookie':"UM_distinctid=1657bef2d89118-0ca65ae184eaf5-47e1039-1fa400-1657bef2d8a12b; Hm_lvt_e4fa146ca527418cd9e1709678bb7628=1535382597; CNZZDATA1271275477=278914166-1535377470-%7C1535382870; Hm_lpvt_e4fa146ca527418cd9e1709678bb7628=1535383002",
                'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13', "Referer":"http://yezmw.com/"}
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
                req.encoding = 'utf-8'
                content = urllib2.urlopen(req, timeout=30).read().decode('utf8', errors='replace')
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
            menu = soup.first("div", {"id":"nav"})
            if menu == None:
                print '没找到对应的频道 ', baseurl
                return None
            lis = menu.findAll("a")
            ret = []
            for a in lis:
                print a
                if a != None and a.text.find('首页') == -1:
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
