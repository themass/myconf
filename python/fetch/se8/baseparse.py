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
#662cf,579cf,298cf
baseurl = "https://www.729cf.com/"
reg = re.compile(r"(.*\/)\d+\.htm")
mp3Name = re.compile(r"<span>.*</span>")
soundUrl = "/yousheng/index.html"
queue = MyQueue.MyQueue(200)
maxCount = 5
videoUrl='http://m.123456xia.com:888'
m3u8regVideo = re.compile(r"varvHLSurl=(.*?)\+'(.*?)';")
regVideo = re.compile(r'generate_down\((.*) \+ "(.*)"\);')
urlMap={"m3u8url_10":"https://768ii.com","m3u8url_24k":"https://768ii.com","m3u8url_new":"https://768ii.com",
        "m3u8url_69":"https://768ii.com","m3u8url_10_2":"https://768ii.com","m3u8url_24k_2":"https://768ii.com",
        "m3u8url_new_2":"https://768ii.com","m3u8url_69_2 ":"https://768ii.com"}
m3u8Map = {"m3u8_host":"https://one.991video.com","m3u8_host1":"https://991video.com","m3u8_host2":"https://mmbfxl1.com"}
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
                    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13', "Referer": baseurl})
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
