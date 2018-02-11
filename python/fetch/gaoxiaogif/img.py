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
import json
from urlparse import urlparse
from fetch.profile import *

reload(sys)
sys.setdefaultencoding('utf8')


class ImgParse(BaseParse):

    def __init__(self,):
        threading.Thread.__init__(self)
        self.t_obj = {}
        self.t_obj['name'] = "搞笑动态图"
        self.t_obj['baseurl'] = baseurl
        self.t_obj['url'] = 'gaoxiaogif.com'
        self.t_obj['updateTime'] = datetime.datetime.now()
        self.t_obj['rate'] = 1.2
        self.t_obj['showType'] = 3
        self.t_obj['channel'] = 'gaoxiao_gif'

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        ops.inertImgChannel(self.t_obj)
        dbVPN.commit()
        # 有分页
        sortType = dateutil.y_m_d()
        for i in range(1, maxImgPage):
            url = '/index.html'
            if i!=1:
                url = url.replace('.html','')+'_'+str(i)+'.html'
            print url
            pics = self.fetchDataHead(url)   
            print '解析',i,'页','len=',len(pics)
            obj = {}
            obj['name'] = pics[0]['text']
            print obj['name']
            obj['channel'] = "gaoxiaogif.com"
            obj['updateTime'] = datetime.datetime.now()
            obj['fileDate'] = ''
            obj['baseurl'] = baseurl
            obj['showType'] = 3
    #             obj['url'] = url.replace("&", "")
            obj['url'] =  sortType+url
    #             obj['pics'] = len(pics)
            obj['pic'] = pics[0]['pic']
            obj['sortType'] = sortType
            obj['pics'] = len(pics)
            ops.inertImgItems(obj)
            for item in pics:
                picitem = {}
                picitem['itemUrl'] = obj['url']
                picitem['picUrl'] = item['pic']
                ops.inertImgItems_item(picitem)
                dbVPN.commit()

    def fetchDataHead(self, url):
        try:
            soup = self.fetchUrl(url)
            alist = []
            divs = soup.findAll("div", {'id': 'bdshare'})
            for div in divs:
                data = div.get('data').replace("'", "\"").replace(",}", "}")
                print data
                alist.append(json.loads(data))
            return alist

        except Exception as e:
            print common.format_exception(e)

    def fetchImgItemData(self, url):
        try:
            soup = self.fetchUrl(url)
            div = soup.first("div",{'class':'listgif-giftu content_pic'})
            if div!=None:
                return div.first("img").get('src')
        except Exception as e:
            print common.format_exception(e)
            return None
