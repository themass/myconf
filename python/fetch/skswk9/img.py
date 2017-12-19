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
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class ImgParse(BaseParse):

    def __init__(self, obj):
        threading.Thread.__init__(self)
        self.t_obj = obj
        self.t_obj['rate'] = 1.1
        self.t_obj['showType'] = 0

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        url_org = self.t_obj['url']
        self.t_obj['url'] = self.t_obj['url'].replace("&", "")
        ops.inertImgChannel(self.t_obj)
        dbVPN.commit()
        channel = self.t_obj['url']
        print self.t_obj['url']
        # 有分页
        for i in range(1, maxImgChannelPage):
            url = self.t_obj['url'] + str(i)
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
            tab = soup.first("table", {'id': 'ajaxtable'})
            if tab != None:
                return tab.findAll('tr', {"class": "tr3 t_one"})
            return []

        except Exception as e:
            print common.format_exception(e)

    def fetchImgItemsData(self, url, channel):
        try:
            trs = self.fetchDataHead(url)
            print url, ";itemsLen=", len(trs)
            objs = []
            sortType = dateutil.y_m_d()
            for item in trs:
                ahrefs = item.findAll("a")
                if ahrefs == None:
                    continue
                for ahref in ahrefs:
                    match = img_channel_title.search(ahref.text)
                    if match == None:
                        continue
                    obj = {}
                    match = img_channel_date.search(ahref.text)
                    if match != None:
                        obj['fileDate'] = match.group(0)
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
                    print 'url=', obj['url'], 'filedate=', obj['fileDate'], '  图片数量=', len(pics)
                    objs.append(obj)
            return objs
        except Exception as e:
            print common.format_exception(e)

    def fetchImgs(self, url):
        soup = self.fetchUrl(url)
        picData = soup.first("div", {"class": "tpc_content"})
        picList = picData.findAll("img")
        pics = []
        for item in picList:
            if item.get('src') != None and item.get('src').endswith("jpg"):
                pics.append(item.get('src'))
        return pics
