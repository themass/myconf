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
import sys,os
reload(sys)
sys.setdefaultencoding('utf8')
# http://www.dehyc.com
baseurl = "http://www.mastv54.com"
aheader = {'Upgrade-Insecure-Requests':"1",'Cookie':"0kJG_2132_saltkey=s0jrJCjU; 0kJG_2132_lastvisit=1527182720; Hm_lvt_8b0de6e47fc88f711248780a73250037=1527186429; 0kJG_2132_atarget=1; 0kJG_2132_st_t=0%7C1527188463%7Cc9fbec5384d03b763077d9150c58d8d8; 0kJG_2132_forum_lastvisit=D_110_1527186763D_41_1527188053D_49_1527188463; 0kJG_2132_sid=yKP5pp; 0kJG_2132_st_p=0%7C1527188676%7C02322face8f21e9a566579c4b1d3d2d7; 0kJG_2132_visitedfid=41D49D110D50; 0kJG_2132_viewid=tid_26280; Hm_lpvt_8b0de6e47fc88f711248780a73250037=1527188783; 0kJG_2132_lastact=1527188676%09home.php%09misc; 0kJG_2132_sendmail=1",'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl}
maxCount = 3
regVideo = re.compile(r"a:'http(.*)m3u8?")
regVideoYun = "/share/"

class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
    def headerHtml(self):
#         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__)) 
        with open("%s/%s"%("mastv54",'header.html')) as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist
    def fetchUrl(self, url):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(baseurl+url, headers={'Cookie':"td_cookie=18446744069599001696; UM_distinctid=16267a77486203-0a34f7eb9f837-454c092b-1fa400-16267a7748726f; CNZZDATA4033785=cnzz_eid%3D1967344694-1522153663-null%26ntime%3D1522153663; CNZZDATA1263493226=2025093065-1522155903-null%7C1522155903; PHPSESSID=cqppj1tg9v8tf27j95ogqogjs1; td_cookie=18446744069599206493; WSKY=6c172; jiathis_rdc=%7B%22http%3A//www.zxdy.cc/vod/22266.html%22%3A1739039602%2C%22http%3A//www.zxdy.cc/play/22266-0-1.html%22%3A1739044927%2C%22http%3A//www.zxdy.cc/Uploads/https%3A//tupian.tupianzy.com/pic/upload/vod/2018-03-03/201803031520062617.jpg%22%3A1739118415%2C%22http%3A//www.zxdy.cc/list/1-p-3-0.html%22%3A1739129605%2C%22http%3A//www.zxdy.cc/list/1-p-1-0.html%22%3A1739216767%2C%22http%3A//www.zxdy.cc/list/9-p-1-0.html%22%3A1739358031%2C%22http%3A//www.zxdy.cc/list/9-p-2-0.html%22%3A1739371664%2C%22http%3A//www.zxdy.cc/Uploads/https%3A//wx3.sinaimg.cn/mw690/005w5c6ogy1fjuo496v5uj30tu15ok3k.jpg%22%3A1739577535%2C%22http%3A//www.zxdy.cc/Uploads/https%3A//img.alicdn.com/imgextra/i4/2264228004/TB2UynHnQqvpuFjSZFhXXaOgXXa_%21%212264228004.jpg%22%3A1739585958%2C%22http%3A//www.zxdy.cc/%22%3A1739586271%2C%22http%3A//www.zxdy.cc/vod/5128.html%22%3A1739763188%2C%22http%3A//www.zxdy.cc/vod/1.html%22%3A1739772004%2C%22http%3A//www.zxdy.cc/play/1-0-1.html%22%3A1739777508%2C%22http%3A//www.zxdy.cc/vod/4063.html%22%3A1739811363%2C%22http%3A//www.zxdy.cc/play/4063-0-2.html%22%3A1739820736%2C%22http%3A//www.zxdy.cc/list/11-p-1-0.html%22%3A1739855919%2C%22http%3A//www.zxdy.cc/vod/22236.html%22%3A0%7C1522158279843%2C%22http%3A//www.zxdy.cc/play/22236-0-1.html%22%3A%220%7C1522158307282%22%7D",
                'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13', "Referer":url})
                req.encoding = 'utf-8'
                response = urllib2.urlopen(req, timeout=300)
                gzipped = response.headers.get(
                    'Content-Encoding')  # 查看是否服务器是否支持gzip
                content = response.read().decode('utf8', errors='replace').replace("<!––>","")
                soup = BeautifulSoup(content)
                return soup
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', baseurl + url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', url
        return BeautifulSoup('')

    def fetchUrlWithBase(self, url):
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

    def fetchContentUrlWithBase(self, url):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(baseurl + url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13', "Referer":baseurl})
                req.encoding = 'utf-8'
                response = urllib2.urlopen(req, timeout=300)
                content = response.read()
                gzipped = response.headers.get(
                    'Content-Encoding')  # 查看是否服务器是否支持gzip
                if gzipped:
                    content = zlib.decompress(
                        content, 16 + zlib.MAX_WBITS)  # 解压缩，得到网页源码
                return content
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', baseurl+url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', baseurl+url
        return ''
# p = BaseParse()
# print p.fetchContentUrlWithBase("/list/?37-1.html", header)