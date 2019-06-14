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

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        objs = self.parseChannel()
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in objs:
            ops.inertImgChannel(obj)
        dbVPN.commit()
        for obj in objs:
            for i in range(1, maxImgPage):
                url= "/%s%s%s"%(obj['url'].replace("1.html",""),i,".html")
                print url
                count = self.update(url, ops, obj['url'], i)
                dbVPN.commit()
                if count == 0:
                    break
    def parseChannel(self):
        ahrefs = self.header("header2.html")
        objs = []
        for ahref in ahrefs:
            obj = {}
            obj['name']= ahref.text
            obj['url']=ahref.get("href")
            obj['baseurl'] = baseurl
            obj['updateTime'] = datetime.datetime.now()
            obj['rate'] = 1.1
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
            return soup.findAll('li',{"class":"col-md-14 col-sm-16 col-xs-12 clearfix news-box"})

        except Exception as e:
            print common.format_exception(e)

    def fetchImgItemsData(self, url, channel):
        try:
            lis = self.fetchDataHead(url)
            print url, ";itemsLen=", len(lis)
            objs = []
            sortType = dateutil.y_m_d()
            for li in lis:
                ahref = li.first("a")
                if ahref!=None:
                    obj = {}
                    obj['name'] = ahref.get("title")
                    obj['url'] = ahref.get('href')
                    obj['fileDate'] = ''
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
                    print 'url=', obj['url'], obj['name'],'filedate=', obj['fileDate'], '  图片数量=', len(pics)
                    objs.append(obj)
            return objs
        except Exception as e:
            print common.format_exception(e)

    def fetchImgs(self, url):
        soup = self.fetchUrl(url)
        picData = soup.first("div",{"class":"details-content text-justify"})
        picList = picData.findAll("img")
        pics = []
        for item in picList:
            if item.get('src') != None and item.get('src').endswith("jpg"):
                pics.append(item.get('src'))
        return pics
