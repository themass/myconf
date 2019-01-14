#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import threading
from common import common
from baseparse import *
from common import db_ops
from common.envmod import *
from common import dateutil
from fetch.profile import *
global baseurl


class ImgParse(BaseParse):

    def __init__(self, obj):
        threading.Thread.__init__(self)
        self.t_obj = obj
        self.t_obj['rate'] = 1.1
        self.t_obj['showType'] = 3
        self.t_obj['channel'] = 'porn_sex'

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        ops.inertImgChannel(self.t_obj)
        dbVPN.commit()
        url = self.t_obj['url']
        channel = url
        first = self.parsFirstPage(url)
        print first, url
        for i in range(1, maxImgPage):
            pageurl = url.replace(".html","-") + str(i) + ".html"
            count = self.update(pageurl, ops, channel, i)
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
            div = soup.first("div",{"class":"box movie_list"})
            if div!=None:
                lis = div.findAll("li")
                return lis
            return []

        except Exception as e:
            print common.format_exception(e)

    def fetchImgItemsData(self, url, channel):
        try:
            lis = self.fetchDataHead(url)
            objs = []
            sortType = dateutil.y_m_d()
            for item in lis:
                ahrefs = item.findAll("a")
                for ahref in ahrefs:
                    obj = {}
                    span = ahref.first('span')
                    if span != None:
                        obj['fileDate'] = span.text
                    else:
                        obj['fileDate'] = ''
                    name = ahref.text.replace(obj['fileDate'], '')
                    obj['name'] = name
                    print name
                    obj['url'] = ahref.get('href')
                    obj['baseurl'] = baseurl
                    obj['channel'] = channel
                    obj['updateTime'] = datetime.datetime.now()
                    pics = self.fetchImgs(ahref.get('href'))
                    if len(pics) == 0:
                        print '没有 图片文件--', ahref, '---', url
                        continue
                    obj['picList'] = pics
                    obj['pics'] = len(pics)
                    obj['sortType'] = sortType
                    obj['showType'] = 3
                    print 'url=', obj['url'], '  图片数量=', len(pics)
                    objs.append(obj)
            return objs
        except Exception as e:
            print common.format_exception(e)

    def fetchImgs(self, url):
        pics = []
        try:
            soup = self.fetchUrl(url)
            picData = soup.first("div", {"class": "content"})
            picList = picData.findAll("img")
            for item in picList:
                pics.append(item.get('data-original'))
            return pics
        except Exception as e:
            return pics
