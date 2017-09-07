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


class ImgGrilParse(BaseParse):

    def __init__(self, obj, queue):
        threading.Thread.__init__(self)
        self.t_obj = obj
        self.t_queue = queue

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        ops.inertImgChannel(self.t_obj)
        dbVPN.commit()
        url = self.t_obj['url']
        channel = url
        self.fetchImgGrilUrl(channel, url)

    def fetchGrilDataHead(self, url):
        try:
            first = self.parsFirstPage(url)
            girls = []
            if first != None:
                for i in range(1, 20):
                    page = first + str(i) + ".htm"
                    items = self.fetchGrilDataHeadPage(page)
                    if items == None:
                        break
                    girls.extend(items)
            else:
                items = self.fetchGrilDataHeadPage(url)
                girls.extend(items)
            return girls
        except Exception as e:
            print common.format_exception(e)

    def fetchGrilDataHeadPage(self, url):
        pageList = []
        soup = self.fetchUrl(url)
        table = soup.find("div", {"class": 'mainArea px17'})
        if table == None:
            return None
        aList = table.findAll("a")
        for item in aList:
            if item.get('href').find("/") != -1:
                pageList.append(item.get('href'))
        return pageList

    def fetchImgGrilUrl(self, url, channel):
        girls = self.fetchGrilDataHead(url)
        for girl in girls:
            self.t_queue.put(ParsImgChannel(girl, url))
#             channels = self.fetchGirlChannel(girl)
#             objs = self.fetchImgItemsData(channels)
#             print "解析 Girl 图片ok----url=", url
#             for obj in objs:
#                 try:
#                     #                     ops.inertImgItems(obj)
#                     print 'items ：', obj
#                     for picItem in obj['picList']:
#                         item = {}
#                         item['itemUrl'] = obj['url']
#                         item['picUrl'] = picItem
# #                         ops.inertImgItems_item(item)
#                         print 'items_item ：', obj
#                 except Exception as e:
#                     print common.format_exception(e)
#             dbVPN.commit()


class ParsImgChannel(BaseParse):

    def __init__(self, obj, url):
        threading.Thread.__init__(self)
        self.t_obj = obj
        self.url = url

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        channels = self.fetchGirlChannel(self.t_obj)
        objs = self.fetchImgItemsData(channels)
        print "解析 Girl 图片ok----url=", self.url
        for obj in objs:
            try:
                ops.inertImgItems(obj)
                print 'items ：', obj['url'], " piclen=", len(obj['picList'])
                for picItem in obj['picList']:
                    item = {}
                    item['itemUrl'] = obj['url']
                    item['picUrl'] = picItem
                    item['origUrl'] = picItem
                    ops.inertImgItems_item(item)
#                     print 'items_item ：', obj
            except Exception as e:
                print common.format_exception(e)
        dbVPN.commit()
        dbVPN.close()

    def fetchGirlChannel(self, url):
        first = self.parsFirstPage(url)
        channels = []
        if first != None:
            for i in range(1, 10):
                page = first + str(i) + ".htm"
                items = self.fetchgirlChannelItems(page)
                if items == None:
                    break
                channels.extend(items)
        else:
            items = self.fetchgirlChannelItems(url)
            channels.extend(items)

        return channels

    def fetchImgItemsData(self, channels):
        try:
            objs = []
            for item in channels:
                sortType = dateutil.y_m_d()
                obj = {}
                obj.update(item)
                obj['baseurl'] = baseurl
                obj['channel'] = self.t_obj
                obj['updateTime'] = datetime.datetime.now()
                pics = self.fetchImgs(obj['url'])
                if len(pics) == 0:
                    print '没有 图片文件--', obj['url']
                    continue
                obj['picList'] = pics
                obj['pics'] = len(pics)
                obj['sortType'] = sortType
                print 'url=', obj['url'], '  图片数量=', len(pics)
                objs.append(obj)
            return objs
        except Exception as e:
            print common.format_exception(e)

    def fetchgirlChannelItems(self, url):
        soup = self.fetchUrl(url)
        div = soup.find("ul", {"class": 'movieList'})
        channels = []
        if div != None:
            alist = div.findAll("a")
            for item in alist:
                obj = {}
                obj['url'] = item.get("href")
                obj['name'] = item.text
                span = item.first('span')
                if span != None:
                    obj['fileDate'] = span.text
                else:
                    obj['fileDate'] = ''
                channels.append(obj)
        return channels

    def fetchImgs(self, url):
        soup = self.fetchUrl(url)
        picData = soup.first("div", {"class": "picContent"})
        if picData == None:
            return []
        picList = picData.findAll("img")
        pics = []
        for item in picList:
            pics.append(item.get('src'))
        return pics
