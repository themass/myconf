#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import threading
from common import common
from baseparse import *
from common import db_ops
from common.envmod import *
from common import dateutil
global baseurl


class ImgParse(BaseParse):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        channels = self.parseChannel()
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for channel in channels:
            ops.inertImgChannel(channel)
        dbVPN.commit()
        for obj in channels:
            url = obj['url']
            channel = url
            for i in range(1, maxPageImg):
                if i == 1:
                    url = url + 'index.html'
                else:
                    url = (url + 'index_%s.html') % (i)
                print url
                count = self.update(url, ops, channel, i)
                dbVPN.commit()
                if count == 0:
                    break

    def parseChannel(self):
        soup = self.fetchUrl(baseurl)
        divs = soup.findAll('div', {"class": "childnav"})
        allChannel = []
        for div in divs:
            alist = div.findAll('a')
            for ahref in alist:
                for need in channel_more:
                    if ahref.get('href').count(need) > 0:
                        print '需要解析的channel=', ahref.get('href')
                        obj = {}
                        obj['name'] = ahref.text
                        obj['baseurl'] = baseurl
                        obj['url'] = ahref.get('href')
                        obj['updateTime'] = datetime.datetime.now()
                        obj['rate'] = 1.2
                        obj['showType'] = 3
                        allChannel.append(obj)
        return allChannel

    def update(self, url, ops, channel, i):
        objs = self.fetchImgItemsData(url, channel)
        print "解析 Img 图片ok----channl=", channel, '  页数=', i, " 数量=", len(objs)
        for obj in objs:
            try:
                ops.inertImgItems(obj)
                for picItem in obj['picList']:
                    item = {}
                    item['itemUrl'] = obj['url']
                    item['picUrl'] = picItem
                    ops.inertImgItems_item(item)
            except Exception as e:
                print common.format_exception(e)
        return len(objs)

    def fetchDataHead(self, url):
        try:
            soup = self.fetchUrl(url)
            div = soup.first("div", {"class": "piclist"})
            if div != None:
                return div.findAll('li')

        except Exception as e:
            print common.format_exception(e)
            return []

    def fetchImgItemsData(self, url, channel):
        objs = []
        try:
            lis = self.fetchDataHead(url)
            sortType = dateutil.y_m_d()
            for item in lis:
                ahref = item.first("a")
                if ahref != None:
                    obj = {}
                    name = item.first("span").text
                    obj['name'] = name
                    print name
                    aurl = ahref.get("href")
                    if aurl.count("http") == 0:
                        aurl = baseurl + aurl
                    obj['url'] = aurl
                    obj['baseurl'] = baseurl
                    obj['channel'] = channel
                    obj['updateTime'] = item.first("b", {"class": "b1"}).text
                    pics = self.fetchImgs(obj['url'])
                    if len(pics) == 0:
                        print '没有 图片文件--', obj['url'], '---', url
                        continue
                    obj['picList'] = pics
                    obj['pics'] = len(pics)
                    obj['sortType'] = sortType
                    print 'url=', obj['url'], '  图片数量=', len(pics)
                    objs.append(obj)
            return objs
        except Exception as e:
            print common.format_exception(e)
            return objs

    def fetchImgs(self, url):
        pics = []
        url = url.replace(".html", "")
        for i in range(1, 70):
            if i == 1:
                fetchUrl = url + ".html"
            else:
                fetchUrl = (url + "_%s.html") % (i)
            print fetchUrl
            soup = self.fetchUrl(fetchUrl)
            active = soup.first("center")
            if active == None:
                print '共 ', i, '页', '---', 'null---', fetchUrl
                continue
            pic = active.first("img")
            pics.append(pic.get('lazysrc'))
#             num = soup.first("span", {"id", "allnum"})
#             print num
#             if str(i) == num:
#                 break

        return pics
