#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import threading
from common.envmod import *
from common import common
from common import db_ops
from baseparse import *
from common import dateutil
from fetch.profile import *

global baseurl

class TextChannelParse(BaseParse):

    def __init__(self):
        pass
    
    def run(self):
        objs = self.textChannel()
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for channel in objs:
            ops.inertTextChannel(channel)
            print channel
        dbVPN.commit()
        dbVPN.close()
        
        
        for item in objs:
            print '开始解析频道---',item
            try:
                channel = item['url']
                for i in range(1, maxTextPage ):
                    page_url = "%s%s"%("/page/",i)
                    print page_url
                    dbVPN = db.DbVPN()
                    ops = db_ops.DbOps(dbVPN)
                    count = self.update(page_url, ops, channel)
                    dbVPN.commit()
                    dbVPN.close()
                    if count == 0:
                        break
            except Exception as e:
                print common.format_exception(e)
    def textChannel(self):
        objs = []
        obj={}
        obj['url']="941novel"
        obj['name']="我爱激情"
        obj['baseurl']=baseurl
        obj['updateTime']=datetime.datetime.now()
        obj['pic']=''
        obj['rate']=1.2
        obj['channel']=obj['url']
        obj['showType']=3
        obj['channelType']='normal'
        objs.append(obj)
        return  objs

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
            div = soup.first("div", {"id": "archive-posts"})
            if div == None:
                print '没有数据', url
                return []
            datalist = div.findAll("h3")
            objs = []
            sortType = dateutil.y_m_d()
            for item in datalist:
                ahref = item.first("a")
                if ahref!=None:
                    try:
                        obj = {}
                        obj['fileDate'] = ''
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
        soup = self.fetchUrlWithBase(url,header)
        data = soup.first("div", {"class": "entry-content clearfix"})
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
