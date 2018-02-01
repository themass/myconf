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
urlList =['/hd','/chinese','/uncensored"']
header = {'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl,
          "Cookie":"rr=http%3A%2F%2Favhd101.info%2F; factory=eyJpdiI6InNGcGY3UHFpZEw3d2swbFwvWjU0d3J3PT0iLCJ2YWx1ZSI6ImxqNGNJazJ4aHBFdUQ1ZWlRWDlCd3c9PSIsIm1hYyI6ImVmODY5NzhhNjYzNTYzOGZkNDliMTllZjhhOTZmMGYzOGQ4MTE2ZThlNGFiZjhlODg4NDAxZGMwZGZiNjgxMWYifQ%3D%3D; factory_title=eyJpdiI6IllKcHFuN05ualI5ZFJuT3p3SXJYeXc9PSIsInZhbHVlIjoiTU9DUkxLMVdqcGpRZ0ZkU2pRK2w2QT09IiwibWFjIjoiNTI3MzQ4YzBlNGY5NmMzNTBkZmIxYjU1OTUxOWJlOWEwNmY1MzhmMzcyYTUwOTFhNzM0Y2FjMTU5YWRiYmJjMCJ9; factory_login_url=eyJpdiI6Ik5DYjBobk5rOXoxQkRRb3JZeExTR1E9PSIsInZhbHVlIjoiclc0ZDlWWk5kMGNTMHA1TEhzZzVWdz09IiwibWFjIjoiNTg1YjU3Zjc1NjZkZjliMDRkNWM2ZDAyZmJlOWQ2YzI1MWQwMGU2YzJlOTg3ZTBmMjBjZDA4ZmU1NTA4Y2MyMiJ9; _ga=GA1.2.574316942.1517505604; _gid=GA1.2.432344268.1517505604; iadult=1; intercom-id-feq323as=71486f20-f8c8-4607-96a4-588e3a9e59ee; XSRF-TOKEN=eyJpdiI6ImhBN1RxYVRwcitDYmVoRGtLVGhJd2c9PSIsInZhbHVlIjoicVVIaXFxUXdKUFI3V3c5RmxUNVV1VFFjcDE0N0kwc2VIWTZxNnhDRm5sT0M5TDBUUUFQRllSOTdKVDBwYXdkZDVUTSthejZ2SzRsWU1GWmFmSDR3RXc9PSIsIm1hYyI6ImJlNmZjOWE5ODVlYmYwYjI0Mzg5NDI2NDRlYzM1NDU2ZmQyZGVjZDQ0ZTBjZWNiNzkyMWYwYmUwYTI0MTAyMzUifQ%3D%3D; miao_ss=eyJpdiI6IlRjNVoyUGY1WTlRMUNiSzk5NUpCakE9PSIsInZhbHVlIjoiZXM1YzZXeXlid2pqR3Jwb2dURGtaaWVyaFBXZ3FNUmR4aXZBaGNnaW9sMUFXMWUyRkhjWkpNTUJjc1pPUjJLTkhsbVJYN3B5NEdxRUQzWDBiZVwvU1VBPT0iLCJtYWMiOiI1MzVlZWFjN2ZlMTgyNjMxNDcxYjA1YTA5ZTZhMDVkYWIwYjgxNDlmODllMWY2ZTcyMzk1MDM3OTIyYjU3N2M5In0%3D; _gat=1"}
maxCount = 3
videoApi = re.compile(r'http(.*).m3u8')
class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def fetchUrl(self, url, aheader=header):
        count = 0
        while count < maxCount:
            try:
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

    