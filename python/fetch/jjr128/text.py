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

max_page = 15


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
        
        for item in channels:
            try:
                channel = item['url']
                page_url = item['url'].replace('.html','')
                for i in range(1, maxPage):
                    
                    url = (page_url+"-pg-%s.html")%(i)
                    count = self.update(url, ops, channel)
                    dbVPN.commit()
                    if count == 0:
                        break
                dbVPN.close()
            except Exception as e:
                print common.format_exception(e)
                dbVPN.commit()
                dbVPN.close()
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
            ret = ops.inertTextItems(obj)
            if ret == None:
                print 'text 已经存在，解析完毕'
                return 0
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
                    obj = {}
                    obj['fileDate'] = item.first('span').text
                    name = ahref.text
                    obj['name'] = name
                    print name
                    obj['url'] = ahref.get('href')
                    obj['baseurl'] = baseurl
                    obj['channel'] = channel
                    obj['updateTime'] = datetime.datetime.now()
                    self.t_queue.put(TextItemContentParse(ahref.get('href')))
                    obj['sortType'] = sortType
                    objs.append(obj)
            return objs
        except Exception as e:
            print common.format_exception(e)


class TextItemContentParse(BaseParse):

    def __init__(self, url):
        threading.Thread.__init__(self)
        self.t_url = url

    def run(self):
        soup = self.fetchUrl(self.t_url)
        data = soup.first("div", {"class": "caoporn_main"})
        print '解析文件 ', self.t_url
        if data != None:
            try:
                obj = {}
                obj['fileUrl'] = self.t_url
                obj['file'] = str(data)
                dbVPN = db.DbVPN()
                ops = db_ops.DbOps(dbVPN)
                ops.inertTextItems_item(obj)
                dbVPN.commit()
                dbVPN.close()
            except Exception as e:
                print common.format_exception(e)
            print self.t_url, ' 解析完成'
#             return str(data)
#         return None
