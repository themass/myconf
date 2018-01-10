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
        for i in range(1, maxImgChannelPage):
            url = '/index.html'
            if i!=1:
                url = self.t_obj['url'].replace('.html','')+'_'+str(i)+'.html'
            print url
            pics = self.fetchDataHead(url)   
            print '解析',i,'页','len=',len(pics)
            for item in pics:
                obj = {}
                obj['name'] = item['text']
                print obj['name']
                obj['channel'] = self.t_obj['url']
                obj['updateTime'] = datetime.datetime.now()
                obj['fileDate'] = ''
                obj['baseurl'] = baseurl
                obj['showType'] = 3
        #             obj['url'] = url.replace("&", "")
                obj['url'] = urlparse(item['pic']).path
        #             obj['pics'] = len(pics)
                obj['pic'] = item['pic']
                obj['sortType'] = sortType
                pics = []
                obj['pics'] = 1
                ops.inertImgItems(obj)
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
                data = div.get('data')
                print data
                alist.append(json.load(data))
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
