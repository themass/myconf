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
            imgitem['name'] = 'gif动态'
            imgitem['url'] = 'ratoo.net/a/gif/'
            imgitem['baseurl'] = baseurl3
            imgitem['channel'] = channel
            imgitem['updateTime'] = datetime.datetime.now()
            imgitem['fileDate'] = ''
            imgitem['showType'] = 3
            imgitem['sortType'] = sortType
            pics = []
            for i in range(1, maxImgPage):
                url = "%s%s%s"%(obj['baseurl'].replace("1.html",''),i,".html")
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
        obj['baseurl']=baseurl3
        obj['updateTime'] = datetime.datetime.now()
        obj['rate'] = 1.2
        obj['showType'] = 3
        obj['channel'] = 'gaoxiao_gif'
        objs.append(obj)
        return objs

    def fetchImgs(self, url):
        pics = []
        soup = self.fetchUrl(url)
        data = soup.findAll("div", {"class": "pic1"})
        for obj in data:
            try:
                ahref = obj.first('a')
                soup = self.fetchUrl('http://www.ratoo.net'+ahref.get('href'))
                img  = soup.first('img',{'id':'bigimg'})
                if img!=None:
                    pics.append('http://www.ratoo.net'+img.get('src'))
            except Exception as e:
                print common.format_exception(e)
        return pics
