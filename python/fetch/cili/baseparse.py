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
import os
baseurl = "https://www.gavbus558.com"
ciliVideo = re.compile(r"magnet(.*?)html")

header = {'Cookie':'UM_distinctid=16529ac59740-084dfe7512bd8e-47e1039-1fa400-16529ac5977243; fikker-4gJQ-VSIJ=MQls4GDSRcImxuLcNJd7NMxLDStI0srq; fikker-4gJQ-VSIJ=MQls4GDSRcImxuLcNJd7NMxLDStI0srq; CNZZDATA1274319095=208496749-1534001853-null%7C1534006406; CNZZDATA1274141679=1940873741-1533998159-null%7C1534007965; fikker-NujU-rLFW=Oktg0GvorcheDc25xWRmRLjSVwb76kBS; fikker-NujU-rLFW=Oktg0GvorcheDc25xWRmRLjSVwb76kBS; fikker-d1fm-MUvU=NQ6e2qFujuVQTo2qtERKx3ICpoH9fchq; fikker-d1fm-MUvU=NQ6e2qFujuVQTo2qtERKx3ICpoH9fchq; fikker-8INA-OGRo=riJqBoXYrU6EpUdOOgpqNktLfEbLLu89; fikker-8INA-OGRo=riJqBoXYrU6EpUdOOgpqNktLfEbLLu89; fikker-Mj9K-O6Kl=cTkDYNQ47bUxNRUnIxaTurmNe8ETiFyT; fikker-Mj9K-O6Kl=cTkDYNQ47bUxNRUnIxaTurmNe8ETiFyT; vcnzdmlusername=themass; vcnzdmluserid=194056; vcnzdmlgroupid=1; vcnzdmlrnd=HcBPFRl3teW9rN8MMoKw; vcnzdmlauth=d8e8ccc200438e3b766af8f7ea6b4bb5; vcnzdcheckplkey=1534011045%2Ce794e15a9307a7c6e49289b21165fa85%2Cd3b151f56d8ec4483d5346e665d2389e','User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl}
maxCount = 3
regVideo = re.compile(r"magnet(.*?)','_self")

class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def fetchUrl(self, url, aheader=header):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(baseurl + url, headers=aheader)
                req.encoding = 'utf-8'
                response = urllib2.urlopen(req, timeout=300)
                gzipped = response.headers.get(
                    'Content-Encoding')  # 查看是否服务器是否支持gzip
                content = response.read().decode('utf8', errors='replace')
                if gzipped:
                    content = zlib.decompress(
                        content, -zlib.MAX_WBITS)  # 解压缩，得到网页源码
                soup = BeautifulSoup(content)
                return soup
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', baseurl + url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', url
        return BeautifulSoup('')
    def header(self,name):
#         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__)) 
        with open("%s/%s"%("cili",name)) as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist
    def fetchUrlWithBase(self, url, aheader=header):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(url, headers=aheader)
                req.encoding = 'utf-8'
                response = urllib2.urlopen(req, timeout=300)
                gzipped = response.headers.get(
                    'Content-Encoding')  # 查看是否服务器是否支持gzip
                content = response.read().decode('utf8', errors='replace')
                if gzipped:
                    content = zlib.decompress(
                        content, -zlib.MAX_WBITS)  # 解压缩，得到网页源码
                soup = BeautifulSoup(content)
                return soup
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试',  url, '次数', count
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
                print '打开页面错误,重试', baseurl+url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', baseurl+url
        return ''

    