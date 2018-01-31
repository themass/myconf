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
import re,os
# http://www.dehyc.com
baseurl = "https://www.2246x.com"
headerUrl='/js/LayoutIt.js'
header = {'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl}
maxCount = 3
maxTextPage=40

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
    def header(self):
#         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__)) 
        with open("x2246/header.html") as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        print content
        soup= BeautifulSoup(content)
        uls = soup.findAll('ul',{'class':'nav_menu'})
        return uls
        
    def headerVideo(self):
        uls = self.header()
        objs = []
        for ul in uls:
            active = ul.first('li',{"class":"active"})
            if active.text.count('小说')==0:
                ahrefs = ul.findAll("a")
                for ahref in ahrefs:
                    obj={}
                    if ahref.get('href')!='/' and ahref.text.count("图片")==0 and ahref.text.count("小说")==0 and ahref.text.count("帮助")==0:
                        obj['url']=ahref.get('href')
                        obj['name']=ahref.text
                        objs.append(obj)
        return objs
    def headerImg(self):
        uls = self.header()
        objs = []
        for ul in uls:
            active = ul.first('li',{"class":"active"})
            if active.text.count('小说')==0:
                ahrefs = ul.findAll("a")
                for ahref in ahrefs:
                    obj={}
                    if ahref.get('href')!='/' and ahref.text.count("图片")!=0:
                        obj['url']=ahref.get('href')
                        obj['name']=ahref.text
                        objs.append(obj)
        return objs
    def headerText(self):
        uls = self.header()
        objs = []
        for ul in uls:
            active = ul.first('li',{"class":"active"})
            if active.text.count('小说')!=0:
                ahrefs = ul.findAll("a")
                for ahref in ahrefs:
                    obj={}
                    if ahref.get('href')!='/':
                        obj['url']=ahref.get('href')
                        obj['name']=ahref.text
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

    def fetchContentUrl(self, url, aheader=header):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(baseurl+url, headers=aheader)
                content = urllib2.urlopen(req, timeout=300).read()
                return content
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', url
        return ''

    