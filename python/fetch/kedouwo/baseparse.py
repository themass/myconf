#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import zlib
import urllib2
import threading
from common.envmod import *
from common import db_ops
from common import common
import threading,ssl
from BeautifulSoup import BeautifulSoup
import re
import os
base_videourl = "?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=post_date&from=%s&_=1551981239756"
baseurl3= "https://www.asy3333.com"
videoId3 = re.compile("/index.php/vod/detail/id/(.*?).html")

#baseurl4 = "http://www.7bam.icu/"
#baseurl7 = "http://117klav.icu/"
#https://bxchua.com
#baseurl8 = "https://bxjiao.com"
#baseurl10 = "https://www.jjj382.com"
baseurl12 = "http://www.tlula44.com"
#baseurl14 = "http://gebi0.com"
#baseurl15 = "https://www.qzi2.com"
header = {'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl3,
          'Cookie':"ASPro_3b178725fc4f483c1b3b540e9254fe69=rjglqktt458s6t79lurudu6u37; __51cke__=; __atuvc=5%7C34; __atuvs=5b7d8978e2390365001; __tins__19260318=%7B%22sid%22%3A%201534952887546%2C%20%22vd%22%3A%2012%2C%20%22expires%22%3A%201534956279466%7D; __tins__18963094=%7B%22sid%22%3A%201534952887602%2C%20%22vd%22%3A%2012%2C%20%22expires%22%3A%201534956279478%7D; __51laig__=27"}
header2 = {'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl3,
          'Cookie':"pxTK_2132_saltkey=CDKD7k08; pxTK_2132_lastvisit=1534866582; _ga=GA1.2.676201030.1534870386; _gid=GA1.2.1608862136.1534870386; Hm_lvt_a7f417c344bdcfebc00a1b4084b35417=1534870386,1534952916; pxTK_2132_sid=mFy09c; pxTK_2132_st_p=0%7C1534955323%7C896e471f57aa95da32adf071ecf4097b; pxTK_2132_viewid=tid_11237; pxTK_2132_st_t=0%7C1534955633%7C29fb8f0eb614b2081f3c458d979f7266; pxTK_2132_forum_lastvisit=D_45_1534955312D_38_1534955633; pxTK_2132_visitedfid=38D45; Hm_lpvt_a7f417c344bdcfebc00a1b4084b35417=1534955838; _gat_gtag_UA_118038554_1=1; pxTK_2132_lastact=1534955633%09home.php%09misc; pxTK_2132_sendmail=1"}
header3 = {'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl3,
          'Cookie':"__cfduid=daf97951d263f43b40aa880057d128ec61534232909; PHPSESSID=df01o1psnjpnr67df4k4q53s50; UM_distinctid=1653768772b33e-00e6b1d3653486-47e1039-1fa400-1653768772c5f; CNZZDATA1274203680=1684804072-1534228697-%7C1534234099",
          "X-Requested-With":"XMLHttpRequest"}
maxCount = 3
regVideo = re.compile(r"src=\"(.*?)\"frameborder")
regVideoM3 = re.compile(r"http(.*?)m3u8")
regVideoM310 = re.compile(r'http(.*?)m3u8"')

regVideoMp4 = re.compile(r"http(.*?)mp4")
regaotu = re.compile("videos/(.*?)/")
lu92_path = re.compile("/?m=vod-detail-id-(.*?).html")
class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def header(self):
#         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__)) 
        with open("kedouwo/header.html") as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist

    def headers(self,name):
#         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__)) 
        with open("kedouwo/"+name) as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist
    def fetchUrl(self, url, aheader=header):
        count = 0
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        while count < maxCount:
            try:
                req = urllib2.Request(url, headers=aheader)
                content = urllib2.urlopen(req, context=ctx,timeout=30).read().decode('utf8', errors='replace').replace("<![endif]-->","").replace("<!--[if lt IE 9]>", "").replace("<![endif]-->", "").replace("<!--[if lt IE 9 ]>","").replace("<![endif]-->","")
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
                req = urllib2.Request(url, headers=aheader)
                content = urllib2.urlopen(req, timeout=300).read()
                return content
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', url
        return ''

    