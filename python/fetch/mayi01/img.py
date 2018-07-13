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
                url = obj['url']
                if i!=1:
                    url= "%s%s%s"%(url.replace("0.html",""),i,".html")
                print url
                count = self.update(url, ops, obj['url'], i)
                dbVPN.commit()
                if count == 0:
                    break
    def parseChannel(self):
        ahrefs = self.header("header3.html")
        objs = []
        for ahref in ahrefs:
            obj = {}
            obj['name']= ahref.text
            obj['url']=ahref.get("href")
            obj['baseurl'] = baseurlImg
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
            soup = self.fetchUrl(baseurlImg+url)
            div = soup.first("div", {"class": "container"})
            if div != None:
                return div.findAll('a')
            return []

        except Exception as e:
            print common.format_exception(e)

    def fetchImgItemsData(self, url, channel):
        try:
            lis = self.fetchDataHead(url)
            print url, ";itemsLen=", len(lis)
            objs = []
            sortType = dateutil.y_m_d()
            for item in lis:
                obj = {}
                obj['name'] = item.first("div",{"class":"float-left"}).text
                print obj['name']
                obj['url'] = item.get('href')
                obj['fileDate'] = item.first("div",{"class":"float-right"}).text
                obj['baseurl'] = baseurlImg
                obj['channel'] = channel
                obj['updateTime'] = datetime.datetime.now()
                pics = self.fetchImgs(item.get('href'))
                if len(pics) == 0:
                    print '没有 图片文件--', item, '---', url
                    continue
                obj['picList'] = pics
                obj['pics'] = len(pics)
                obj['sortType'] = sortType
                obj['showType'] = 3
                print 'url=', obj['url'], 'filedate=', obj['fileDate'], '  图片数量=', len(pics)
                objs.append(obj)
            return objs
        except Exception as e:
            print common.format_exception(e)

    def fetchImgs(self, url):
        soup = self.fetchUrl(baseurlImg+url)
        picData = soup.first("div", {"class": "imgList"})
        picList = picData.findAll("img")
        pics = []
        for item in picList:
            if item.get('src') != None and item.get('src').endswith("jpg"):
                pics.append(item.get('data-original'))
        return pics
