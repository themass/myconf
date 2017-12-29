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

    def __init__(self, obj):
        threading.Thread.__init__(self)
        self.t_obj = obj
        self.t_obj['rate'] = 1.1
        self.t_obj['showType'] = 0

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        ops.inertImgChannel(self.t_obj)
        dbVPN.commit()
        url = self.t_obj['url']
        channel = url
        for i in range(1, maxPageImg):
            url = (url + imgPageurl) % (i)
            print url
            count = self.update(url, ops, channel, i)
            dbVPN.commit()
            if count == 0:
                break

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
            divs = soup.findAll("div", {"class": "block"})
            return divs

        except Exception as e:
            print common.format_exception(e)

    def fetchImgItemsData(self, url, channel):
        objs = []
        try:
            divs = self.fetchDataHead(url)
            sortType = dateutil.y_m_d()
            for item in divs:
                imgDiv = item.first("div", {"class": "media-image"})
                print imgDiv
                if imgDiv != None:
                    obj = {}
                    name = item.first(
                        "div", {"class": "block-layer block-inner"}).first("a").text
                    obj['name'] = name
                    obj['url'] = imgDiv.first("a").get("href")
                    obj['baseurl'] = baseurl
                    obj['channel'] = channel
                    obj['updateTime'] = datetime.datetime.now()
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
        for i in range(1, 100):
            fetchUrl = (url + imgUrl) % (i)
            soup = self.fetchUrl(fetchUrl)
            active = soup.first("li", {"class": "active"})
            if active == None or active.first("a").text != str(i):
                print '共 ', i, '页'
                break
            picList = soup.findAll(
                "img", {"class": "img img-responsive lazyimage"})
            for item in picList:
                pics.append(baseurl + item.get('data-src'))

        return pics
