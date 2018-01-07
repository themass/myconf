#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import threading
from common.envmod import *
from common import common
from common import db_ops
from baseparse import *
from common import dateutil
global baseurl

class TextChannelParse(BaseParse):

    def __init__(self,queue):
        self.t_queue=queue
    
    def run(self):
        ahrefs = self.fetchHead('小说')
        channels = self.parsChannelText(ahrefs)
        
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for channel in channels:
            ops.inertTextChannel(channel)
            print channel
        dbVPN.commit()
        dbVPN.close()
        
        
        for item in channels:
            print '开始解析频道---',item
            try:
                channel = item['url']
                page_url = item['url'].replace('.html','')
                for i in range(1, maxPage):
                    
                    url = (page_url+"-pg-%s.html")%(i)
                    dbVPN = db.DbVPN()
                    ops = db_ops.DbOps(dbVPN)
                    count = self.update(url, ops, channel)
                    dbVPN.commit()
                    dbVPN.close()
                    if count == 0:
                        break
            except Exception as e:
                print common.format_exception(e)
    def parsChannelText(self, ahrefs):
        objs = []
        for ahref in ahrefs:
            obj = {}
            obj['name'] = ahref.text
            obj['baseurl'] = baseurl
            obj['url'] = ahref.get('href')
            obj['updateTime'] = datetime.datetime.now()
            objs.append(obj)
        return objs

    def update(self, url, ops, channel):
        objs = self.fetchTextData(url, channel)
        print "解析Txt小说 ok----channl=", channel, '  数量=', len(objs)
        for obj in objs:
            try:
                ret = ops.inertTextItems(obj)
                if ret == None:
                    print 'text 已经存在，解析完毕'
            except Exception as e:   
                print  common.format_exception(e)
        return len(objs)

    def fetchTextData(self, url, channel):
        try:
            soup = self.fetchUrl(url)
            div = soup.first("div", {"class": "list_art"})
            if div == None:
                print '没有数据', url
                return []
            datalist = div.findAll("li")
            objs = []
            sortType = dateutil.y_m_d()
            for item in datalist:
                ahref = item.first("a")
                if ahref!=None:
                    try:
                        obj = {}
                        obj['fileDate'] = item.first('span').text
                        name = ahref.text
                        obj['name'] = name
                        print name
                        obj['url'] = ahref.get('href')
                        obj['baseurl'] = baseurl
                        obj['channel'] = channel
                        obj['updateTime'] = datetime.datetime.now()
#                         self.t_queue.put(TextItemContentParse(ahref.get('href')))
                        ret = self.fetchText(ahref.get('href'))
                        if ret==None:
                            print '没有文章数据',ahref.get('href')
                            continue
                        obj['sortType'] = sortType
                        objs.append(obj)
                    except Exception as e:   
                        print  common.format_exception(e)
            return objs
        except Exception as e:
            print common.format_exception(e)
    def fetchText(self,url):
        soup = self.fetchUrl(url)
        data = soup.first("div", {"class": "caoporn_main"})
        if data != None:
            try:
                obj = {}
                obj['fileUrl'] = url
                obj['file'] = str(data)
                dbVPN = db.DbVPN()
                ops = db_ops.DbOps(dbVPN)
                ops.inertTextItems_item(obj)
                dbVPN.commit()
                dbVPN.close()
                print '解析文件 ', url,'完成'
                return 1
            except Exception as e:
                print common.format_exception(e)
        return None
        
#             print self.t_url, ' 解析完成'
#             return str(data)
#         return None
