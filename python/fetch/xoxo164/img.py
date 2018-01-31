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
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        objs = self.imgChannel()
        for obj in objs:
            ops.inertImgChannel(obj)
        dbVPN.commit()
       
        for obj in objs:
            url = obj['url']
            channel = url
            for i in range(1, maxImgPage):
                url = "%s%s%s"%(url.replace('1.html',''),i,'.html')
                print url
                count = self.update(url, ops, channel, i)
                dbVPN.commit()
                if count == 0:
                    break
    def imgChannel(self):
        soup = self.fetchUrl('/')
        uls = soup.findAll('ul',{'class':'nav_menu clearfix'})
        print uls
        channelList =[]
        for ul in uls:
            ul.first('li',{'class':'active'})
            print ul.text
            if ul!=None :
                a = ul.first('a')
                if a!=None and (a.text=='图片专区'):
                    ahrefs = ul.findAll('a')
                    for ahref in ahrefs:
                        if ahref.get('href')!='/':
                            obj={}
                            obj['name']=ahref.text
                            obj['url']=ahref.get('href')
                            obj['baseurl']=baseurl
                            obj['updateTime']=datetime.datetime.now()
                            obj['pic']=''
                            obj['rate']=1.2
                            obj['channel']='porn_sex'
                            obj['showType']=3
                            channelList.append(obj)
        return channelList
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
        objs = []
        try:
            soup= self.fetchUrl(url)
            sortType = dateutil.y_m_d()
            div = soup.first('div',{'class':'box list channel'})
            if div!=None:
                lis = div.findAll('li')
                for item in lis:
                    ahref = item.first("a")
                    if ahref != None:
                        obj = {}
                        udate= ahref.first('span').text
                        name = ahref.text.replace(udate,'')
                        obj['name'] = name
                        obj['url'] = ahref.get("href")
                        obj['baseurl'] = baseurl
                        obj['channel'] = channel
                        obj['updateTime'] = datetime.datetime.now()
                        pics = self.fetchImgs(obj['url'])
                        if len(pics) == 0:
                            print '没有 图片文件--', obj['url'], '---', url
                            continue
                        obj['picList'] = pics
                        obj['pics'] = len(pics)
                        obj['sortType'] = sortType
                        obj['showType'] = 3
                        print 'url=', obj['url'], '  图片数量=', len(pics)
                        objs.append(obj)
                return objs
        except Exception as e:
            print common.format_exception(e)
            return objs

    def fetchImgs(self, url):
        pics =[]
        soup= self.fetchUrl(url)
        div = soup.first('div',{'class':'content'})
        if div!=None:
            imgs = div.findAll('img')
            for img in imgs:
                pics.append(img.get('src'))
        return pics
