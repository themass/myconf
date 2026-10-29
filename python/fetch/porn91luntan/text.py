#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import threading
import re
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
                for i in range(1, maxTextPage):
                    page_url = item['url']
                    page_url = "%s&page=%s"%(page_url,i)
                    print page_url
                    dbVPN = db.DbVPN()
                    ops = db_ops.DbOps(dbVPN)
                    count = self.update(page_url, ops, channel,item['name'])
                    dbVPN.commit()
                    dbVPN.close()
                    if count == 0:
                        break
            except Exception as e:
                print common.format_exception(e)
    def textChannel(self):
        objs = []
        ahrefs = self.header()
        for ahref in ahrefs:
            obj = {}
            obj['name']=ahref.text
            obj['url']=ahref.get('href')
            obj['baseurl']=baseurl
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1.2
            obj['channel']=obj['url']
            obj['showType']=3
            obj['channelType']='normal'
            objs.append(obj)
        return objs

    def update(self, url, ops, channel,name):
        objs = self.fetchTextData(url, channel,name)
        print "解析Txt小说 ok----channl=", channel, '  数量=', len(objs)
        for obj in objs:
            try:
                ret = ops.inertTextItems(obj)
                if ret == None:
                    print 'text 已经存在，解析完毕'
            except Exception as e:   
                print  common.format_exception(e)
        return len(objs)

    def fetchTextData(self, url, channel,name):
        try:
            soup = self.fetchUrl(url if url.startswith('http') else baseurl+url)
            datalist = soup.findAll("th",{"class":"subject new"})
            # Some forum pages use class='subject common' for pinned/new
            # topics.  Include those too, while filtering out the header row.
            if not datalist:
                datalist = soup.findAll("th", {"class": "subject"})
                datalist = [item for item in datalist
                            if item.find("a", href=re.compile("viewthread\\.php\\?tid="))]
            objs = []
            sortType = dateutil.y_m_d()
            for subject in datalist:
                if subject is not None:
                    # The href and actual title are on the nested <a>.  The
                    # parent <th> contains view count/author/date metadata.
                    title_link = subject.find(
                        'a', href=re.compile(r'^viewthread\.php\?tid='))
                    if title_link is None:
                        continue
                    itemUrl = title_link.get('href')
                    title = title_link.text.strip()
                    try:
                        obj = {}
                        obj['fileDate'] = '1111'
                        obj['name'] = title
                        print obj['name'], itemUrl
                        obj['url'] = itemUrl
                        obj['baseurl'] = baseurl
                        obj['channel'] = channel
                        obj['updateTime'] = datetime.datetime.now()
#                         self.t_queue.put(TextItemContentParse(itemUrl))
                        ret = self.fetchText(itemUrl)
                        if ret is None:
                            print '没有文章数据', itemUrl
                            continue
                        obj['sortType'] = sortType
                        obj['channelName'] = name
                        objs.append(obj)
                    except Exception as e:
                        print common.format_exception(e)
            return objs
        except Exception as e:
            print common.format_exception(e)
    def fetchText(self,url):
        if url ==None:
            return None
        soup = self.fetchUrl(url if url.startswith('http') else baseurl+url)
        data = soup.findAll("div", {"class": "t_msgfontfix"})
        if data:
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
