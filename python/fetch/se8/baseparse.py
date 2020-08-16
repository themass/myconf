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
reload(sys)
sys.setdefaultencoding('utf8')
#662cf,579cf,298cf,v5c5
baseurl = "https://www.445ffbc74f8a.com/"
reg = re.compile(r"(.*\/)\d+\.htm")
mp3Name = re.compile(r"<span>.*</span>")
soundUrl = "/yousheng/index.html"
queue = MyQueue.MyQueue(200)
maxCount = 5
videoUrl='http://m.123456xia.com:888'
#m3u8regVideo = re.compile(r"varvHLSurl=(.*?)\+'(.*?)';")

m3u8regVideo = re.compile(r"varvideo='(.*?)\.m3u8';")
mp4regVideo = re.compile(r"varvideo='(.*?)\.mp4';")
regVideo = re.compile(r'generate_down\((.*) \+ "(.*)"\);')
urlMap={"m3u8url_10":"https://768ii.com","m3u8url_24k":"https://768ii.com","m3u8url_new":"https://768ii.com",
        "m3u8url_69":"https://768ii.com","m3u8url_10_2":"https://768ii.com","m3u8url_24k_2":"https://768ii.com",
        "m3u8url_new_2":"https://768ii.com","m3u8url_69_2 ":"https://768ii.com"}
m3u8Map = {"m3u8_host":"https://s1.maomibf1.com","m3u8_host1":"https://s1.maomibf1.com","m3u8_host2":"https://s1.maomibf1.com"}
rmbvideoUrl='http://555.maomixia555.com:888'
rmbregVideo = re.compile(r'generate_down\((.*) \+ "(.*)"\);')
class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def fetchUrl(self, url):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(baseurl + url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13', "Referer": baseurl,'Cookie':' _ga=GA1.2.330215259.1593160900; Hm_lvt_3543e29c6ddfec226d134afef16f9f54=1593160900,1593349888; Hm_lvt_f343b6d40a7d6aeb9c7e1dc87ffbd27c=1593160900,1593349888; _gid=GA1.2.1460935595.1593349888; runno=1; tiaoss=0; _gat_gtag_UA_159847605_3=1; _gat_gtag_UA_159847605_4=1; Hm_lpvt_3543e29c6ddfec226d134afef16f9f54=1593353637; Hm_lpvt_f343b6d40a7d6aeb9c7e1dc87ffbd27c=1593353637; playss=18'})
                req.encoding = 'utf-8'
                response = urllib2.urlopen(req, timeout=300)
                gzipped = response.headers.get(
                    'Content-Encoding')  # 查看是否服务器是否支持gzip
                content = response.read()
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
                print '打开页面错误,重试', baseurl + url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', baseurl + url
        return BeautifulSoup('')

    def fetchHead(self, name):
        try:
            url = "index/home.html"
            soup = self.fetchUrl(url)
            menus = []
            menus.extend(soup.findAll("div", {"class": "row-item even"}))
            menus.extend(soup.findAll("div", {"class": "row-item odd"}))
            for menu in menus:
                active = menu.first("div", {"class":"row-item-title bg_red"}).text
                if active.count(name) > 0:
                    return menu.findAll("li")
        except Exception as e:
            print common.format_exception(e)

    def parsHeadText(self, lis):
        data = {}
        objs = []
        for li in lis:
            a = li.first("a")
            if a.get("href") != "/":
                data[a.get("href")] = a.text
        for url, name in data.items():
            obj = {}
            obj['name'] = name
            obj['baseurl'] = baseurl
            obj['url'] = url
            obj['updateTime'] = datetime.datetime.now()
            objs.append(obj)
        return objs

    def parsFirstPage(self, url):
        soup = self.fetchUrl(url)
        divs = soup.findAll("div", {"class": "pagination"})
        if len(divs) > 0:
            aAll = divs[len(divs) - 1].findAll("a")
            for a in aAll:
                if a.text.count(u"上一页") > 0:
                    href = a.get('href')
                    match = reg.search(href)
                    if match == None:
                        return None
                    if match.group(1).replace(" ", "") == "":
                        return None
                    return match.group(1)
        else:
            divs = soup.findAll("div", {"class": "pageList"})
            if len(divs) > 0:
                aAll = divs[len(divs) - 1].findAll("a")
                for a in aAll:
                    if a.text.count(u"上一页") > 0:
                        href = a.get('href')
                        match = reg.search(href)
                        if match == None:
                            return None
                        return match.group(1)
        return None
