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
baseurl = "https://cn.jav101.com"
header = {'Cookie':'__cfduid=d028cd7ecebe311b5dc96efb9c6417e1e1534871899; locale=cn; TPWY_JAV_AV_referer=aHR0cDovL3d3dy5iYWl4aW5nc2Uub3JnLw%3D%3D; _ga=GA1.2.1716130975.1534871905; CloudFront-Key-Pair-Id=APKAJBW3QQCETPXK5WRQ; _gid=GA1.2.628182036.1534959226; CloudFront-Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9zYXQuamF2MTAxLmNvbS8qL2ludHJvLyoiLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE1MzQ5NzEwMjF9fX1dfQ__; CloudFront-Signature=kxQWnzGFS2xTCoQk2NaLiIMGXHNymQyl4N67NM7ck8nwSiXAaLlOjyWVaUFJVKwAQBSSaR4wEXSE6tkakMvLnEXgqIjdNzZaU0bU621nawxd428LKXIPbY1mY9c8YWHOz%7EySLYaJRtkjd0twRnamMCSKB4Y1ITcqLYiHJtEjeHE%7E8w-3qL%7Eoft8%7EbiN5Rr2UK7h6Z-yyos2t5IP0w5mWsd5PETOkGN1zvPLpIju33wfQTTBpgk-1hCUpvn-NRkBqf2CLkaO3AO0YWYojAVFstthclA9Fva5Ow%7E4MvMjBu-LRkFJ2PcMyCAqbMzmZLPw9Feuno%7EHT2wUQ-ocoPssMrw__; XSRF-TOKEN=eyJpdiI6IkRaaFZqTTM2K1dTXC9RTmIzYXNOY1N3PT0iLCJ2YWx1ZSI6ImF1XC95ZE9nRDlkZzBVVUFiK25lTXE3anJiUUVYT0ZsOEJcL1UzR092UGhmaU5NVzFWbEx5QmRcL3FYMnFGaFN5SDlkQjBoTlB5N21ERktiY0lCWWRxRWRBPT0iLCJtYWMiOiI5YTU2YjUxYjFkYzE1ZDU3Yjc1NDMwZjMwZTc3MjBjNGE4MjMwYmIzNGU1MGQxOGI4ZTA3NzZhNDM1YTNmNzI3In0%3D; laravel_session=eyJpdiI6IlVGbDQ4dytEMXBBZFJcLzJCUHZGR05RPT0iLCJ2YWx1ZSI6InNPRTJTc21BeHl0cytcLzRLUzFEZklJUU56d21xdVp2eWlOK2RBWXVRcEtLcWxJa1k4SWFWc0ZcLzRodndyUHlEN01PSlE2N0FTdm94RjdzVGd4bDZLdFE9PSIsIm1hYyI6ImI0OGZlMTY0OTBhODAyYmE1MGVjZGM1YWQxNDExNzM4MGQ2MDFmYjc5OWM0NDg3Y2MwYWMyYjNjMjZjYTc3MzQifQ%3D%3D; _ceg.s=pdvivw; _ceg.u=pdvivw','User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl}
maxCount = 3
regVideo = re.compile(r"http(.*?)m3u8")
regVideo2 = re.compile(r"mac_url=unescape\('(.*?)'\);")

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
    def header(self):
#         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__)) 
        with open("lusibi/header.html") as f:
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
                print '打开页面错误,重试', baseurl+url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', baseurl+url
        return ''

    