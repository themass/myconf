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
baseurl = "https://cn.av101.ws"
baseurl2="https://avhd101.com"
#'/hd','/chinese',
urlList =['/uncensored']
header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl2,
          "Cookie":"__cfduid=dd4573f23e457274464ab236132a125081548501565; locale=cn; _ga=GA1.2.82358204.1548501415; CloudFront-Key-Pair-Id=APKAJBW3QQCETPXK5WRQ; _gid=GA1.2.1124505462.1550395968; XSRF-TOKEN=eyJpdiI6ImJoQ2xLbnQ1Y0lGRyt4MmhEbWtRSkE9PSIsInZhbHVlIjoiYk9LWFJDc3BWamE5NHhVZllSVVNPRm81dk9HTSt2dFdpbkUzZ0RjajlMdU5ZazA5TTlVdVR1N3lpdzNUZlBIZSIsIm1hYyI6ImZhYWNlMzhmMjMzMDc5ZGFjNTk3MTA2NmIyMDE5Yzg4MDA5MDI1M2UxNmM2MDE2MzI5ZjVmMmJjNWQyNDYyZjUifQ%3D%3D; jav101_sessions=eyJpdiI6Ik9aMnJwMUJkaWtTa1RkdzVqY1lhelE9PSIsInZhbHVlIjoieUpUQnliRjA2ckVTODFPZXZmdlwvOGc4KzgrM1ZxY1BySXdPK1FMaitwZDFGTmdzM2luMTBzczVYVHdqeldQaHUiLCJtYWMiOiIxMzdlMjUwNjRlZjVkMGJjY2YzYmFiNjhmOTdkMjRhMGM5NjViMjJhOTM4NTQxNDAwNjExZmQ4ZmIyNTg3MTkyIn0%3D; CloudFront-Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9zYXQuamF2MTAxLmNvbS8qL2ludHJvLyoiLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE1NTA0MjI0NjJ9fX1dfQ__; CloudFront-Signature=T0mo8pDUVoHYIPOmAka8Y0pNg7l2MY7OqbaX3ELwTPeAsGqFO3LeVqLkuiIr3V9lhlpdPsmuoiu4vXmqpuZxvXiRWhhkgBND1xFX7H~XANstMiTkbiFQ9ZGBu5cjuM5ZHBuXEkEQaL4GWwBaQO6Z04CSob5F8gTwm41LbPOOrHP1YIRGRFecVjxU1PFARzf3LxoRBMlztu4x4mC0WmrXXe-uE9g0i9cUXelRQ-yTMBMIGZrPq0FbiVyte3VDRRxUVltdrTkPg5Ic~o~5F5ul6v5ln4p24So~RAXAUfmii6DyEeNxYvgJE3vDfbhIwTeoHVh21M2aFzl3RmoMJ9fKFA__; _gat_UA-51244524-6=1; _gat_UA-51244524-1=1; _gat_UA-99293918-19=1"}
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

    