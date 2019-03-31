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
baseurl = "http://www.papa345.com"
base_videourl = "?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=post_date&from=%s&_=1551981239756"
baseurl2= "https://www.v88hd.space/"
baseurl3= "https://www.asy1000.com"
videoId3 = re.compile("vod-detail-id-(.*?).html")

baseurl4 = "http://www.7mav4.club/"
baseurl5 = "http://www.hnav01.xyz/"
baseurl6 = "http://www.91av02.club/"
baseurl7 = "http://115klav.icu/"
baseurl8 = "https://7648x.com/"
baseurl9 = "https://www.91uu9.com"
baseurl10 = "https://www.jjj382.com"
baseurl11 = "https://www.kpl023.com"
baseurl12 = "http://www.tlula44.com"
baseurl13 = "http://www.caca049.com"
baseurl14 = "http://gebi0.com"

header = {'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl,
          'Cookie':"ASPro_3b178725fc4f483c1b3b540e9254fe69=rjglqktt458s6t79lurudu6u37; __51cke__=; __atuvc=5%7C34; __atuvs=5b7d8978e2390365001; __tins__19260318=%7B%22sid%22%3A%201534952887546%2C%20%22vd%22%3A%2012%2C%20%22expires%22%3A%201534956279466%7D; __tins__18963094=%7B%22sid%22%3A%201534952887602%2C%20%22vd%22%3A%2012%2C%20%22expires%22%3A%201534956279478%7D; __51laig__=27"}
header2 = {'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl2,
          'Cookie':"pxTK_2132_saltkey=CDKD7k08; pxTK_2132_lastvisit=1534866582; _ga=GA1.2.676201030.1534870386; _gid=GA1.2.1608862136.1534870386; Hm_lvt_a7f417c344bdcfebc00a1b4084b35417=1534870386,1534952916; pxTK_2132_sid=mFy09c; pxTK_2132_st_p=0%7C1534955323%7C896e471f57aa95da32adf071ecf4097b; pxTK_2132_viewid=tid_11237; pxTK_2132_st_t=0%7C1534955633%7C29fb8f0eb614b2081f3c458d979f7266; pxTK_2132_forum_lastvisit=D_45_1534955312D_38_1534955633; pxTK_2132_visitedfid=38D45; Hm_lpvt_a7f417c344bdcfebc00a1b4084b35417=1534955838; _gat_gtag_UA_118038554_1=1; pxTK_2132_lastact=1534955633%09home.php%09misc; pxTK_2132_sendmail=1"}
header3 = {'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl3,
          'Cookie':"__cfduid=daf97951d263f43b40aa880057d128ec61534232909; PHPSESSID=df01o1psnjpnr67df4k4q53s50; UM_distinctid=1653768772b33e-00e6b1d3653486-47e1039-1fa400-1653768772c5f; CNZZDATA1274203680=1684804072-1534228697-%7C1534234099",
          "X-Requested-With":"XMLHttpRequest"}
header4 = {'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl4,
          'Cookie':"__cfduid=db7f29cd10852fa511d1e0668e89d05001534872686; UM_distinctid=1655d8a8baa6f6-003fe3a1f827f5-47e1039-1fa400-1655d8a8bac102; ASPro_8af8761312ef191adf2017005f0d1eed=0vnasb2ejvpc1d3bquf7lt6vc7; __atuvc=1%7C34; CNZZDATA1274401056=2115274732-1534871498-null%7C1535039855"}
header5 = {'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl4,
          'Cookie':"UM_distinctid=1655d8a945d4b3-04cf9c8cfb02c4-47e1039-1fa400-1655d8a945e132; PHPSESSID=tefc4f836ibs5s166aht5lvtp3; __51cke__=; CNZZDATA1273155436=2112313512-1534871260-null%7C1535037844; ggy_second=true; __tins__3892343=%7B%22sid%22%3A%201535038199894%2C%20%22vd%22%3A%201%2C%20%22expires%22%3A%201535039999894%7D; __tins__19380135=%7B%22sid%22%3A%201535038188896%2C%20%22vd%22%3A%203%2C%20%22expires%22%3A%201535040034907%7D; __51laig__=4"}
header6 = {'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl4,
          'Cookie':"__cfduid=d44aa5159886044d753c8806d83e7539b1535038342; AVS=17jbicrqspfve3rn2gplbkpqk0; __51cke__=; UM_distinctid=165676aaa8164a-0532684d1256a1-47e1039-1fa400-165676aaa8f449; pgv_pvi=869407744; pgv_si=s269490176; __atuvc=1%7C34; CNZZDATA1271838784=1655185687-1535036227-null%7C1535041056; __tins__19458827=%7B%22sid%22%3A%201535044802928%2C%20%22vd%22%3A%206%2C%20%22expires%22%3A%201535046712534%7D; __tins__19308590=%7B%22sid%22%3A%201535044803126%2C%20%22vd%22%3A%206%2C%20%22expires%22%3A%201535046712562%7D; __51laig__=20"}
header7 = {'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl4,
          'Cookie':"__cfduid=d04442510987cdc4647a03da1d8179ba61535135932; UM_distinctid=1656d3b55a10-0e0c6e23061c6c-47e1039-1fa400-1656d3b55a84a1; CNZZDATA1273905787=288757623-1535132900-%7C1535132900; PHPSESSID=5hfhpl7sbdl52hn6mfpq0ee3l1; security_session_verify=2879be1fd96735a49761b2ea855bdc65"}
header8 = {'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl4,
          'Cookie':"__cfduid=d04442510987cdc4647a03da1d8179ba61535135932; UM_distinctid=1656d3b55a10-0e0c6e23061c6c-47e1039-1fa400-1656d3b55a84a1; CNZZDATA1273905787=288757623-1535132900-%7C1535132900; PHPSESSID=5hfhpl7sbdl52hn6mfpq0ee3l1; security_session_verify=2879be1fd96735a49761b2ea855bdc65"}

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
    def header2(self):
#         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__)) 
        with open("kedouwo/header2.html") as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist
    def header3(self):
#         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__)) 
        with open("kedouwo/header3.html") as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist
    def header5(self):
#         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__)) 
        with open("kedouwo/header5.html") as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist
    def header6(self):
#         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__)) 
        with open("kedouwo/header6.html") as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist
    def header7(self):
#         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__)) 
        with open("kedouwo/header7.html") as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist
    def header8(self):
#         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__)) 
        with open("kedouwo/header8.html") as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist
    def header9(self):
#         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__)) 
        with open("kedouwo/header9.html") as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist
    def header10(self):
#         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__)) 
        with open("kedouwo/header10.html") as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist
    def header11(self):
#         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__)) 
        with open("kedouwo/header11.html") as f:
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

    