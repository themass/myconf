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
baseurl = "http://cn.ax98.ws"
baseurl2="https://avhd101.com"
#'/hd','/chinese',
urlList =['/uncensored']
header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl2,
          "Cookie":"__cfduid=dab87d8d3ff06f25571093a51dfe93cc41530380218; rr=direct; iadult=1; XSRF-TOKEN=eyJpdiI6ImZcL0Zha1lzdTZTV3BNeVRabkEwcnJnPT0iLCJ2YWx1ZSI6IlR3Rm41SWswTm5BOVwvXC90aGJPc3EyVDRQc3d5bEVtR3dwakNkVkFzWWZIOXNJU2ZJbFh2d3JOZEtLWEJPMHJrWVRcL2ZIVVlVMXZKeEkrOFJ3Z2ZFUFdnPT0iLCJtYWMiOiI2NTUzOWU4MDY4MzQ1M2NmMjIwNjEwMGJmYTIxN2Y0ZjAyZDlkMzQ0YmZiZjhjZjIwNGFjNjI5YTY5OTAzODc4In0%3D; miao_ss=eyJpdiI6Ik5sMEdydXgybXdhWEF3Mm9uTnlsREE9PSIsInZhbHVlIjoiUjQ5REl4aCtyMElIZTJtYW9zQkUweU9sS0k0NGo5VGFKZkx4Rmw0SmhhQnRKRmlIZWp2ZGVCdUpqalh6ZW1hRzkzVGdxUkdLbXp1NHdVdDhyNVAxakE9PSIsIm1hYyI6IjNhMGE4Njc5NTFjZWI1NzY2MWU5MWM5Nzg3ODhlMzJmYjAzYmQ5YWI0ZmNmNzg1ZDU2MzVmMGJjZGI4OGFjOWYifQ%3D%3D; _ga=GA1.2.1048330161.1530380229; _gid=GA1.2.1000051012.1530380229; _gat_gtag_UA_78207029_1=1"}
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

    