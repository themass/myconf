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
            channel = obj['name']
            page_url = obj['url']
            for i in range(1, maxImgPage):
                url= "%spage_%s.html"%(page_url,i)
                print url
                count = self.update(url, ops, channel, i)
                dbVPN.commit()
                if count == 0:
                    break

    def parseChannel(self):
        ahrefs = self.header("header5.html")
        objs = []
        for ahref in ahrefs:
            print '需要解析的channel=', ahref.get('href')
            obj = {}
            obj['name'] = ahref.text
            obj['baseurl'] = baseurl
            obj['url'] = ahref.get('href')
            obj['updateTime'] = datetime.datetime.now()
            obj['rate'] = 1.2
            obj['showType'] = 3
            obj['channel'] = 'porn_sex'
            objs.append(obj)
        return objs

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
        soup = self.fetchUrl(url)
        datalist = soup.findAll("div",{"class":"grid_item"})
        objs = []
        sortType = dateutil.y_m_d()
        for item in datalist:
            ahref = item.first("a")
            if ahref!=None:
                try:
                    obj = {}
                    name = ahref.text
                    obj['url'] = ahref.get('href')
                    obj['baseUrl'] = baseurl
                    obj['channel'] = channel
                    obj['updateTime'] = datetime.datetime.now()
                    obj['fileDate'] = ''
                    data = self.fetchImgs(obj['url'])
                    if len(data['pic']) == 0:
                        print '没有 图片文件--', obj['url'], '---', url
                        continue
                    obj['picList'] = data['pic']
                    obj['showType'] = 3
                    obj['pics'] = len(data['pic'])
                    obj['name'] = data['name']
                    obj['sortType'] = sortType
                    print obj['name'],'url=', obj['url'],data['pic'][0], '  图片数量=', len(data['pic'])
                    objs.append(obj)
                except Exception as e:
                    print common.format_exception(e)
        return objs

    def fetchImgs(self, url):
        datasrc = {}
        pics = []
        soup = self.fetchUrl(url)
        data = soup.first("div", {"class": "set_column"})
        if data != None:
            try:
                imgs = data.findAll('img')
                for img in imgs:
                    pics.append(img.get('data-src').replace("?max-age=3600",""))
                datasrc['pic']=pics
                h1 = soup.first("h1",{"class":"h1"})
                datasrc['name']= ''
                if h1!=None:
                    texts = h1.text.split("发表")
                    datasrc['name']=texts[0]
            except Exception as e:
                print common.format_exception(e)
        return datasrc
