#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import urllib2
import threading
from common.envmod import *
from common import db_ops
from common import common
from common import httputil
import threading
from BeautifulSoup import BeautifulSoup
import re
from urlparse import urlparse
baseurl = "https://oxxvideo.com/"
videoUrl = 'https://oxxvideo.com/watch?v=%s&page=%s'
channel = 'self_oxxvideo'
header = {'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": "https://oxxvideo.com"}
maxPage = 30
maxCount = 3
regVideo = re.compile(r'{ type: "application/x-mpegurl", src:"(.*)" }')


def parseData(page):
    param = {}
    param['pagesize'] = 30
    param['datatype'] = 'json'
    param['page'] = page
    objs = httputil.getData(baseurl, param, header)
    data = objs.get('data', [])
    dataList = []
    for item in data:
        obj = {}
        obj['name'] = item.get('title', "")
        obj['url'] = item.get('video', "")
        if obj['url'] == '':
            continue
        obj['pic'] = item.get('snapshot', "")
        obj['channel'] = channel
        obj['rate'] = '1.2'
        videourl = urlparse(obj['url'])
        obj['path'] = videourl.path
        obj['updateTime'] = datetime.datetime.now()
        dataList.append(obj)
    return dataList


def parseVideoUrl(page, id):
    count = 0
    while count < maxCount:
        try:
            url = videoUrl % (id, page)
            req = urllib2.Request(url, headers=header)
            content = urllib2.urlopen(req, timeout=300).read()
            soup = BeautifulSoup(content)
            return soup
        except Exception as e:
            print common.format_exception(e)
            print '打开页面错误,重试', baseurl + url, '次数', count
            count = count + 1

    print '打开页面错误,重试3次还是错误', url
    return BeautifulSoup('')
