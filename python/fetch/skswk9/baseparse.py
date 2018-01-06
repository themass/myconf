#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import urllib2
import threading
from BeautifulSoup import BeautifulSoup
from common import common
from common import MyQueue
import re
import sys
import zlib
reload(sys)
sys.setdefaultencoding('utf8')
baseurl = "http://1024.skswk9.pw/pw/"
img_channel_title = re.compile(r"\[[0-9]+P\]")
img_channel_date = re.compile(r"\[[0-9\.]+\]")
img_channels = {"唯美写真": "thread.php?fid=14&page=", "露出激情": "thread.php?fid=16&page=",
                "网友自拍": "thread.php?fid=15&page=", "偷窥原创": "thread.php?fid=49&page="}
queue = MyQueue.MyQueue(20000)
maxCount = 5
maxImgChannelPage = 5


class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def fetchUrl(self, url):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(baseurl + url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13', "Referer": "https://www.bbb670.com/htm/index.htm"})
                req.encoding = 'utf-8'
                response = urllib2.urlopen(req, timeout=300)
                gzipped = response.headers.get(
                    'Content-Encoding')  # 查看是否服务器是否支持gzip
                content = response.read().decode('utf8', errors='replace')
                if gzipped:
                    content = zlib.decompress(
                        content, 16 + zlib.MAX_WBITS)  # 解压缩，得到网页源码
                soup = BeautifulSoup(content)
                return soup
            except Exception as e:
                print '打开页面错误,重试', baseurl + url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', baseurl + url
        return BeautifulSoup('')
