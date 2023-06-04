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
import ssl,os
reload(sys)
sys.setdefaultencoding('utf8')
baseurl = "https://yi2212.cc/pw/"

maxCount = 5
class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def fetchUrl(self, baseurl,url):
        count = 0
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        while count < maxCount:
            try:
                req = urllib2.Request(baseurl+url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13', "Referer": baseurl})
                req.encoding = 'utf-8'
                response = urllib2.urlopen(req, context=ctx,timeout=60)
                gzipped = response.headers.get(
                    'Content-Encoding')  # 查看是否服务器是否支持gzip
                content = response.read().decode('utf8', errors='replace').replace("<![endif]-->","").replace("<!--[if lt IE 9]>", "").replace("<!---连接---->","").replace("<![endif]-->", "").replace("<!--","").replace(" -->","")
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

    def fetchdyi2212Head(self, baseurl,name):
        try:
            soup = self.fetchUrl(baseurl,"/")
            menus = soup.findAll("a")
            channels=[]
            for item in menus:
                if item.get('href')!="/" and item.get('href')!="#":
                    obj={}
                    obj['name']=item.text
                    obj['url']=item.get('href')
                    obj['baseurl']=baseurl
                    channels.append(obj)
            return channels
        except Exception as e:
            print common.format_exception(e)
    def header(self,name):
#         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__)) 
        with open("%s/%s"%("noval1024",name)) as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist
