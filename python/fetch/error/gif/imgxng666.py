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
            dbVPN.commit()
            imgitem = {}
            imgitem['name'] = 'gif动态'
            imgitem['url'] = 'forum-47-1.html'
            imgitem['baseurl'] = baseurl5
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
                if i%5==0:
                    imgitem['picList'] = pics
                    imgitem['pics'] = len(pics)
                    imgitem['pic'] = pics[0]
                    imgitem['url'] = '%s%s'%('xng666.com/a/gif/',i)
                    ops.inertImgItems(imgitem)
                    dbVPN.commit()
                    print '一次提交',imgitem['url'],len(pics)
                    try:
                        for picItem in imgitem['picList']:
                            item = {}
                            item['itemUrl'] = imgitem['url']
                            item['picUrl'] = picItem
                            ops.inertImgItems_item(item)
                        dbVPN.commit()
                    except Exception as e:
                        print common.format_exception(e)
                    pics=[]
        dbVPN.commit()
    def parseChannel(self):
        objs = []
        obj={}
        print '需要解析的channel=', obj.get('url')
        obj['name']='恩爱哈哈哈'
        obj['url']='xiee_GIF'
        obj['baseurl']=baseurl5
        obj['updateTime'] = datetime.datetime.now()
        obj['rate'] = 1.2
        obj['showType'] = 3
        obj['channel'] = 'gaoxiao_gif'
        objs.append(obj)
        return objs

    def fetchImgs(self, url):
        pics = []
        soup = self.fetchUrl(url)
        imgs = soup.findAll("img")
        for img in imgs:
            try:
                if img.get("src").count("http")>0:
                    pics.append(img.get('src'))
            except Exception as e:
                print common.format_exception(e)
        return pics
