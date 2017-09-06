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

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        ops.inertImgChannel(self.t_obj)
        dbVPN.commit()
        url = self.t_obj['url']
        channel = url
        first = self.parsFirstPage(url)
        print first, url
        if first != None:
            for i in range(1, 500):
                url = first + str(i) + ".htm"
                count = self.update(url, ops, channel, i)
                dbVPN.commit()
                if count == 0:
                    break
        else:
            self.update(url, ops, channel)
            dbVPN.commit()

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
            lis = soup.findAll("li")
            return lis

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
                    print 'url=', obj['url'], '  图片数量=', len(pics)
                    objs.append(obj)
            return objs
        except Exception as e:
            print common.format_exception(e)

    def fetchImgs(self, url):
        soup = self.fetchUrl(url)
        picData = soup.first("div", {"class": "picContent"})
        picList = picData.findAll("img")
        pics = []
        for item in picList:
            pics.append(item.get('src'))
        return pics
