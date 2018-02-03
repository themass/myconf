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
reload(sys)
sys.setdefaultencoding('utf8')
class ImgParse(BaseParse):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        channels = self.parseChannel()
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        sortType = dateutil.y_m_d()
        for obj in channels:
            channel = obj['url']
            url = obj['baseurl']
            ops.inertImgChannel(obj)
            imgitem = {}
            imgitem['name'] = '搞笑gif动态'
            imgitem['url'] = 'hugao8.com/category/gao-gif/'
            imgitem['baseurl'] = baseurl2
            imgitem['channel'] = channel
            imgitem['updateTime'] = datetime.datetime.now()
            imgitem['fileDate'] = ''
            imgitem['showType'] = 3
            imgitem['sortType'] = sortType
            pics = []
            for i in range(1, maxImgPage):
                if i!=1:
                    url = "%s%s%s%s"%(obj['baseurl'],"page/",i,"/")
                imgs = self.fetchImgs(url)
                print len(imgs),url
                pics.extend(imgs)
                if len(imgs)==0:
                    break
            imgitem['picList'] = pics
            imgitem['pics'] = len(pics)
            imgitem['pic'] = pics[0]
            ops.inertImgItems(imgitem)
            try:
                for picItem in imgitem['picList']:
                    item = {}
                    item['itemUrl'] = obj['url']
                    item['picUrl'] = picItem
                    ops.inertImgItems_item(item)
            except Exception as e:
                print common.format_exception(e)
    
    def parseChannel(self):
        objs = []
        obj={}
        print '需要解析的channel=', obj.get('url')
        obj['name']='邪恶GIF'
        obj['url']='xiee_GIF'
        obj['baseurl']=baseurl2
        obj['updateTime'] = datetime.datetime.now()
        obj['rate'] = 1.2
        obj['showType'] = 3
        obj['channel'] = 'gaoxiao_gif'
        objs.append(obj)
        return objs

    def fetchImgs(self, url):
        pics = []
        soup = self.fetchUrl(url)
        data = soup.findAll("div", {"class": "picBox"})
        for obj in data:
            try:
                img = obj.first('img')
                pics.append(img.get('src'))
            except Exception as e:
                print common.format_exception(e)
        return pics
