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
baseurl = "http://www.tianjiyy123.com/"
header={'Cookie':"td_cookie=18446744069599001696; UM_distinctid=16267a77486203-0a34f7eb9f837-454c092b-1fa400-16267a7748726f; CNZZDATA4033785=cnzz_eid%3D1967344694-1522153663-null%26ntime%3D1522153663; CNZZDATA1263493226=2025093065-1522155903-null%7C1522155903; PHPSESSID=cqppj1tg9v8tf27j95ogqogjs1; td_cookie=18446744069599206493; WSKY=6c172; jiathis_rdc=%7B%22http%3A//www.zxdy.cc/vod/22266.html%22%3A1739039602%2C%22http%3A//www.zxdy.cc/play/22266-0-1.html%22%3A1739044927%2C%22http%3A//www.zxdy.cc/Uploads/https%3A//tupian.tupianzy.com/pic/upload/vod/2018-03-03/201803031520062617.jpg%22%3A1739118415%2C%22http%3A//www.zxdy.cc/list/1-p-3-0.html%22%3A1739129605%2C%22http%3A//www.zxdy.cc/list/1-p-1-0.html%22%3A1739216767%2C%22http%3A//www.zxdy.cc/list/9-p-1-0.html%22%3A1739358031%2C%22http%3A//www.zxdy.cc/list/9-p-2-0.html%22%3A1739371664%2C%22http%3A//www.zxdy.cc/Uploads/https%3A//wx3.sinaimg.cn/mw690/005w5c6ogy1fjuo496v5uj30tu15ok3k.jpg%22%3A1739577535%2C%22http%3A//www.zxdy.cc/Uploads/https%3A//img.alicdn.com/imgextra/i4/2264228004/TB2UynHnQqvpuFjSZFhXXaOgXXa_%21%212264228004.jpg%22%3A1739585958%2C%22http%3A//www.zxdy.cc/%22%3A1739586271%2C%22http%3A//www.zxdy.cc/vod/5128.html%22%3A1739763188%2C%22http%3A//www.zxdy.cc/vod/1.html%22%3A1739772004%2C%22http%3A//www.zxdy.cc/play/1-0-1.html%22%3A1739777508%2C%22http%3A//www.zxdy.cc/vod/4063.html%22%3A1739811363%2C%22http%3A//www.zxdy.cc/play/4063-0-2.html%22%3A1739820736%2C%22http%3A//www.zxdy.cc/list/11-p-1-0.html%22%3A1739855919%2C%22http%3A//www.zxdy.cc/vod/22236.html%22%3A0%7C1522158279843%2C%22http%3A//www.zxdy.cc/play/22236-0-1.html%22%3A%220%7C1522158307282%22%7D",
                'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13', "Referer":baseurl}
maxCount = 3
regVideo = re.compile(r"http(.*?)m3u8")


class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def fetchUrl(self, url, aheader={}):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(baseurl + url,headers=header)
                req.encoding = 'utf-8'
                response = urllib2.urlopen(req, timeout=300)
                content = response.read().decode('utf8', errors='replace')
                soup = BeautifulSoup(content)
                return soup
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', baseurl + url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', url
        return BeautifulSoup('')

    def fetchUrlWithBase(self, url, aheader={}):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(url,headers=header)
                req.encoding = 'utf-8'
                response = urllib2.urlopen(req, timeout=300)
                content = response.read().decode('utf8', errors='replace')
                soup = BeautifulSoup(content)
                return soup
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', url
        return BeautifulSoup('')

    def fetchContentUrlWithBase(self, url, aheader={}):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(url,headers=header)
                req.encoding = 'utf-8'
                response = urllib2.urlopen(req, timeout=300)
                content = response.read().decode('utf8', errors='replace')
                return content
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', baseurl+url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', baseurl+url
        return ''

    