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
baseurl = "https://333av.vip"
reg = re.compile(r"(.*)index(.*)\.html")
regPage = '<div id="pages">(.*)</div>'
regImg = '<img(.*)/>'
queue = MyQueue.MyQueue(20000)
maxCount = 5
maxImgChannelPage = 100
maxTextChannelPage = 150


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
                count = count + 1

        print '打开页面错误,重试3次还是错误', baseurl + url
        return BeautifulSoup('')

    def fetchHead(self, clasz):
        try:
            url = "/index.html"
            ul_clasz = "navmenu %s" % (clasz)
            print ul_clasz
            soup = self.fetchUrl(url)
            menu = soup.first("div", {"class": ul_clasz})
            if menu == None:
                print '没找到对应的频道 ', ul_clasz
                return None
            lis = menu.findAll("li", "item")
            ret = []
            for li in lis:
                a = li.first('a')
                print a
                if a != None and a.text.find('首页') == -1:
                    row = {}
                    row['name'] = a.text
                    row['baseurl'] = baseurl
                    row['url'] = a.get('href')
                    row['updateTime'] = datetime.datetime.now()
                    ret.append(row)
            return ret
        except Exception as e:
            print common.format_exception(e)

    def parsFirstPage(self, url):
        soup = self.fetchUrl(url)
        divs = soup.findAll("div", {"id": "pages"})
        if len(divs) > 0:
            aAll = divs[len(divs) - 1].findAll("a")
            for a in aAll:
                if a.text.count(u"尾页") > 0:
                    href = a.get('href')
                    match = reg.search(href)
                    if match == None:
                        return None
                    return match.group(2)
        return None

    def removePage(self, data):
        data = re.sub(regPage, '', data)
        return re.sub(regImg, '', data)