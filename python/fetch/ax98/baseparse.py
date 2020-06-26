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
baseurl = "https://cn.av101.net"
baseurl2="https://avhd101.com"
#'/hd','/chinese',
urlList =['/uncensored']
header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl2,
          "Cookie":"__cfduid=d9030517c4200f99b894b4b9aee7798e91548612603; iadult=1; hello=1; _ga=GA1.2.1704361487.1548612614; XSRF-TOKEN=eyJpdiI6Ik5CcnAwbks1a1pSN2U1RzlTaExpRHc9PSIsInZhbHVlIjoia1huZFVCUEp1aE9UaWd3czhhOTZvT01MNXoyN0dWaEpFSHBFMDRYaEVuWnV0dG94dVpBOUdXeWhXZ2RBU0dGNDVMSU9JUjZoOFE4YmkwcUNvcU1tWUE9PSIsIm1hYyI6IjQzZTEzOWZmN2U2NDkzNTc1M2U3YTc5OGNiOTM5YzBkNTFlMDAyZDdiNDkzZGIwOTgxMDI2MTEzYmZkYzQzMTAifQ%3D%3D; miao_ss=eyJpdiI6IjcramZ6eFhHK0RaYWdRWUVlRTdaUlE9PSIsInZhbHVlIjoiVmh6SXdMb09PTmhTZHpaSDk1U3RSeWxKcmVcL3huZnV5OEdlMTd5Y3dnb0ZhUGFDb3ZNb1pSOTZvUDZCbzFEdktoQ1I4THlHeDZkd3ZcL3FLVld1YTF6dz09IiwibWFjIjoiMTYxMTMwZDhhOWU1ZTYyNWQ1MmY3ZWNjOWRlZjlmNjA1MTE1YWUwZmExODI2YzExMTI5ZTI2NzJiMzAzY2UzNSJ9; fp=c301bffae91db7e75ef27e250c698f39.1550590684; _gid=GA1.2.1842292293.1550590687"}
maxCount = 3
videoApi = re.compile(r'http(.*).m3u8')
class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def fetchUrl(self, url, aheader=header):
        count = 0
        while count < maxCount:
            try:
                print baseurl2+url
                req = urllib2.Request(baseurl2 + url, headers=aheader)
                content = urllib2.urlopen(req, timeout=5000).read()
                soup = BeautifulSoup(content)
                return soup
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', baseurl2 + url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', url
        return BeautifulSoup('')
    def fetchUrl2(self, url, aheader=header):
        count = 0
        while count < maxCount:
            try:
                print baseurl+url
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

    