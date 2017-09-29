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
#         ops.inertImgChannel(self.t_obj)
#         dbVPN.commit()
        url = self.t_obj['url']
        objs = self.fetchImgGrilChannel(url)
        for obj in objs:
            # and obj['url'].find('tubaobao.htm') == -1
            if obj['url'].find('/') != -1:
                ops.inertImgChannel(obj)
                self.t_queue.put(ParsImgChannel(obj))
                print '更新channel 完成，chennel数据事件加入队列,', obj['url']
            else:
                print '错误的url', obj
        dbVPN.commit()
        dbVPN.close()
    # 每一项都当成一个channel

    def fetchImgGrilChannel(self, url):
        soup = self.fetchUrl(url)
        objs = []
#         div = soup.find("div", {"class": 'wrap mt20'})
#         if div == None:
#             print '没有 channel:', url
#             return None
        table = soup.find('table')
        if table == None:
            print '没有 channel:', url
            return None
        aList = table.findAll('a')
        for item in aList:
            obj = {}
            obj['url'] = item.get('href')
            obj['baseurl'] = baseurl
            print str(item)
            img = item.find('img')
            if img != None:
                obj['pic'] = img.get('src')
            else:
                obj['pic'] = None
            obj['updateTime'] = dateutil.y_m_d()
            obj['rate'] = 1.4
            obj['showType'] = 1
            obj['name'] = self.fetchImgGrilChannelName(item.get('href'))
            print obj
            objs.append(obj)
        return objs

    def fetchImgGrilChannelName(self, url):
        soup = self.fetchUrl(url)
        p = soup.find("span", {"class": 'cat_pos_l'})
        if p != None:
            return p.text.replace("您的位置：", "").replace(" ", "")
        return "girl"


class ParsImgChannel(BaseParse):

    def __init__(self, obj):
        threading.Thread.__init__(self)
        self.t_obj = obj

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        objs = self.fetchGirlChannelData()
        print "解析 Girl channel图片ok----channel=", self.t_obj['url'], ' size=', len(objs)
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

    def fetchGirlChannelData(self):
        first = self.parsFirstPage(self.t_obj['url'])
        objs = []
        if first != None:
            for i in range(1, 10):
                page = first + str(i) + ".htm"
                items = self.fetchgirlChannelItems(page)
                if items == None:
                    break
                objs.extend(items)
        else:
            items = self.fetchgirlChannelItems(self.t_obj['url'])
            objs.extend(items)
        return objs

    def fetchgirlChannelItems(self, url):
        soup = self.fetchUrl(url)
        div = soup.find("ul", {"class": 'movieList'})
        objs = []
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
                obj['channel'] = self.t_obj['url']
                obj['updateTime'] = dateutil.y_m_d()
                obj['baseurl'] = baseurl
                pics = self.fetchImgs(item.get("href"))
                obj['pics'] = len(pics)
                obj['picList'] = pics
                objs.append(obj)
        return objs

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
