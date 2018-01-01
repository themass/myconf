#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import threading
from common import common
from baseparse import *
from common import db_ops
from common.envmod import *
from common import dateutil
from common import html_parse
global baseurl
nameStr = r"<.*>"

max_page = 80


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
        table = soup.find('table')
        if table == None:
            print '没有 channel:', url
            return None
        aList = table.findAll('a')
        for item in aList:
            obj = {}
            obj['url'] = item.get('href')
            obj['baseurl'] = baseurl
            img = item.find('img')
            if img != None:
                obj['pic'] = img.get('src')
            else:
                obj['pic'] = None
            obj['updateTime'] = dateutil.y_m_d()
            obj['rate'] = 1.4
            obj['showType'] = 0
            obj['name'] = self.fetchImgGrilChannelName(item.get('href'))
            objs.append(obj)
        return objs

    def fetchImgGrilChannelName(self, url):
        soup = self.fetchUrl(url)
        p = soup.find("a", {"class": 'on'})
        if p != None:
            return p.text.replace("您的位置：", "").replace("首页", "").replace(" ", "").replace("&nbsp;", '')
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
                sortType = dateutil.y_m_d()
                obj['sortType'] = sortType
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
            for i in range(1, max_page):
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
        div = soup.find("div", {"class": 'box movie_list'})
        objs = []
        if div != None:
            ul = div.find('ul')
            if ul != None:
                alist = ul.findAll("a")
                for item in alist:
                    if item.get("href").count("tubaobaolist") > 0:
                        objs.extend(self.fetchTubaobaoList(item.get("href")))
                        continue
                    obj = self.fetchgirlChannelItemsOne(item)
                    objs.append(obj)
        return objs

    def fetchTubaobaoList(self, url):
        soup = self.fetchUrl(url)
        div = soup.find("div", {"class": 'box list channel'})
        objs = []
        if div != None:
            ul = div.find('ul')
            if ul != None:
                alist = ul.findAll("a")
                for item in alist:
                    obj = self.fetchgirlChannelItemsOne(item)
                    objs.append(obj)
        return objs

    def fetchgirlChannelItemsOne(self, item):
        obj = {}
        obj['url'] = item.get("href")
        strName = item.text.replace(
            "[if lt IE 9 ]>", "").replace("<![endif]", "")
        obj['name'] = html_parse.filter_tags(strName)
        span = item.first('span')
        if span != None:
            obj['fileDate'] = html_parse.filter_tags(span.text.replace(
                "[if lt IE 9 ]>", "").replace("<![endif]", ""))
            obj['name'] = obj['name'].replace(obj['fileDate'], '')
        else:
            obj['fileDate'] = ''
        obj['channel'] = self.t_obj['url']
        obj['updateTime'] = dateutil.y_m_d()
        obj['baseurl'] = baseurl
        pics = self.fetchImgs(item.get("href"))
        obj['pics'] = len(pics)
        obj['picList'] = pics
        return obj

    def fetchImgs(self, url):
        soup = self.fetchUrl(url)
        picData = soup.first("div", {"class": "content"})
        if picData == None:
            return []
        picList = picData.findAll("img")
        pics = []
        for item in picList:
            pics.append(item.get('src'))
        return pics
