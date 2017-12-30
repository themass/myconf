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
        ops.inertImgChannel(self.t_obj)
        dbVPN.commit()
        # 有分页
        sortType = dateutil.y_m_d()
        channel = self.t_obj['url']
        for name, url in img_channels.items():
            obj = {}
            obj['name'] = name
            obj['channel'] = channel
            obj['updateTime'] = datetime.datetime.now()
            obj['fileDate'] = ''
            obj['baseurl'] = baseurl
            obj['url'] = url.replace("&", "")
#             obj['pics'] = len(pics)
            obj['sortType'] = sortType
            pics = []
            for i in range(1, maxImgChannelPage):
                url = url + str(i)
                alist = self.fetchDataHead(url)
                for item in alist:
                    pic = self.fetchImgItemData(item.get("href"))
                    if pic == None:
                        continue
                    pics.append(pic)
            obj['picList'] = pics
            obj['pics'] = len(pics)
            ops.inertImgItems(obj)
            for picItem in obj['picList']:
                item = {}
                item['itemUrl'] = obj['url']
                item['picUrl'] = picItem
                ops.inertImgItems_item(item)
            dbVPN.commit()

    def fetchDataHead(self, url):
        try:
            soup = self.fetchUrl(url)
            alist = []
            divs = soup.first("div", {'class': 'spacer'})
            if divs != None:
                for div in divs:
                    alist.append(div.first("a"))
            return alist

        except Exception as e:
            print common.format_exception(e)

    def fetchImgItemData(self, url):
        try:
            soup = self.fetchUrl(url)
            aList = soup.findAll("a")
            for item in aList:
                span = item.first("span", {"class": "imgLink"})
                if span == None:
                    continue
                imgSoup = self.fetchUrl(item.get('href'))
                return baseurl + imgSoup.first("img")
        except Exception as e:
            print common.format_exception(e)
            return None
