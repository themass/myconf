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
reload(sys)
sys.setdefaultencoding('utf8')
baseurl = "https://www.eee993.com"
reg = re.compile(r"(.*\/)\d+\.htm")
mp3Name = re.compile(r"<span>.*</span>")
queue = MyQueue.MyQueue(200)
maxCount = 5


class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def fetchUrl(self, url):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(baseurl + url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13', "Referer": "https://www.bbb670.com/htm/index.htm"})
                content = urllib2.urlopen(req, timeout=300).read()
                soup = BeautifulSoup(content)
                return soup
            except Exception as e:
                print '打开页面错误,重试', baseurl + url, '次数', count

        print '打开页面错误,重试3次还是错误', baseurl + url
        return BeautifulSoup('')

    def fetchHead(self, name):
        try:
            url = "/htm/index.htm"
            soup = self.fetchUrl(url)
            menus = soup.findAll("ul", {"class": "menu mt5"})
            for menu in menus:
                active = menu.first("li", "active").text
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
