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
header = {'remote-ip':'47.88.7.156','User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl2,
          "Cookie":" factory=eyJpdiI6InI5Nk1VMFZ6U29CTnU1VDlweFNlYUE9PSIsInZhbHVlIjoicTZkQnlNREI0QktMWjF4UkZ0V0ZRdz09IiwibWFjIjoiYTM2ZTEzYmVjOGNmNWI4ZTYzNzhkNjEwODZkZmNkNmZiZGFmNGZkMjA3ZTI5MmJmMDBhOWYzZGI4YjE0ZmIzYSJ9; factory_title=eyJpdiI6IkV2cHRHcFRmVVVlSTM0dGhKNjFNU2c9PSIsInZhbHVlIjoiYXRSNzFaajJnTTlFSmhBSWdKT1lIUT09IiwibWFjIjoiNWQwNzliMDY4YmI3ZDFkMmIxYTdlYzJiOWQ2NjFlMDZlMjI0YWJiZTRmMjIwYzUxOTdiYzE0NDAzODA5ZDhlYSJ9; factory_login_url=eyJpdiI6Iit6Nmh0eGFcL2J4UTNKKzI0MExZYVdBPT0iLCJ2YWx1ZSI6IlUxcFNscGlCY21hQTI3VHNiOG54c1E9PSIsIm1hYyI6IjE2ZjMwYTU3YmRkZDZjYmZjZDlhNjJlOTExMGRjZTFmMDZiNzc3Y2E2ZGI1ZDZkZWQyM2U1OTk2ODYwNmMyYTIifQ%3D%3D; intercom-id-feq323as=34407766-c3d0-435f-802f-4eca33fdcf7b; __cfduid=d82a4fc08e3190e0b7d7664bbcab710ce1530377596; _ga=GA1.2.1978612400.1530377594; _gid=GA1.2.1627138027.1530377594; rr=https://cn.ax98.ws/; _gat_gtag_UA_78207029_1=1; XSRF-TOKEN=eyJpdiI6Im1xRldpV2J3TUNHTjdPaUJabG5abWc9PSIsInZhbHVlIjoiSUtPSFB2Rm5YU0dkbUxsd1NkS1hGNWtmRUlSb1dncTlhZTZRdU9cL0ErdldoVmxTdGN5QnRJdFI5SHppeVNOcGloNStJbjBEUnVVcEZCWjJxTjlmaHZnPT0iLCJtYWMiOiJkZGYyODgzOGM0ZGYyZWMxYjE1OTFlZGE5ZmUzOWI4NmFjNzU0YzdjZDFlM2EzYWE2MWZlMWU5NzUyNjI2NTFiIn0%3D; miao_cn=eyJpdiI6IkVJbytQalk3Rlp1bkZrcTRudGxmc1E9PSIsInZhbHVlIjoic2ZGUHoyb2pNWVRoQ2NDYlNJYVwvOEJ1SEt1T0t4YkUyQUF5SzlwaDdJOU1BbkhqZDU0bEhHV2hCd0JhR2szcE1wbnhrWWRVUDNPcjVZT0hGYzl5R0F3PT0iLCJtYWMiOiI1MDMxMDIxYzVhYmE3MjE4ZDkyNDhlNjdkZWE1ODI5NTY3MjczODVjNjQ5ZDU2N2M4MjgzOWNlNzUyODVmZGQ4In0%3D"}
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

    