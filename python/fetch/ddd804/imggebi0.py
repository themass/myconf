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
from urllib import unquote
class ImgParse(BaseParse):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        channels = self.parseChannel()
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in channels:
            channel = obj['name']
            page_url = obj['url']
            obj['url']=obj['name']
            ops.inertImgChannel(obj)
            for i in range(1, maxImgPage):
                url = page_url.replace("-pg-1","-pg-"+str(i))
                print url
                count = self.update(url, ops, channel, i)
                dbVPN.commit()

    def parseChannel(self):
        ahrefs = self.header("header3.html")
        objs = []
        for item in ahrefs:
            print '需要解析的channel=', item.get('href')
            obj={}
            obj['name']='隔壁老王'
            obj['url']=item.get('href')
            obj['baseurl']=baseurl13
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

    def fetchImgItemsData(self, url, channel):
        soup = self.fetchUrl(baseurl13,url)
        div = soup.first("li", {"class": "box list channel"})
        objs = []
        sortType = dateutil.y_m_d()
        if div!=None:
            lis = div.findAll("li")
            for item in lis:
                ahref = item.first("a")
                if ahref!=None:
                    try:
                        obj = {}
                        obj['fileDate'] = ''
                        obj['name'] = ahref.get("title")
                        obj['url'] = ahref.get('href')
                        obj['baseurl'] = baseurl13
                        obj['channel'] = channel
                        obj['updateTime'] = datetime.datetime.now()
                        
                        pics = self.fetchImgs(obj['url'])
                        if len(pics) == 0:
                            print '没有 图片文件--', obj['url'], '---', url
                            continue
                        obj['picList'] = pics
                        obj['showType'] = 3
                        obj['pics'] = len(pics)
                        obj['sortType'] = sortType
                        print name,pics[0],'  url=', obj['url'], '  图片数量=', len(pics)
                        objs.append(obj)
                    except Exception as e:
                        print common.format_exception(e)
        return objs

    def fetchImgs(self, url):
        pics = []
        soup = self.fetchUrl(baseurl13,url)
        data = soup.first("div", {"class": "content"})
        if data != None:
            try:
                imgs = data.findAll('img')
                for img in imgs:
                    pics.append(unquote(str(img.get('src'))))
            except Exception as e:
                print common.format_exception(e)
        return pics
