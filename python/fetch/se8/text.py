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

max_page = 500


class TextChannelParse(BaseParse):

    def __init__(self, obj, queue):
        threading.Thread.__init__(self)
        self.t_obj = obj
        self.t_queue = queue

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        ops.inertTextChannel(self.t_obj)
        dbVPN.commit()
        print self.t_obj
        try:
            url = self.t_obj['url']
            channel = url
            first = self.parsFirstPage(url)
            print first, url
            if first != None:
                for i in range(1, max_page):
                    url = first + str(i) + ".htm"
                    count = self.update(url, ops, channel)
                    dbVPN.commit()
                    if count == 0:
                        break
            else:
                self.update(url, ops, channel)
                dbVPN.commit()

            dbVPN.close()
        except Exception as e:
            print common.format_exception(e)
            dbVPN.commit()
            dbVPN.close()

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
            datalist = soup.findAll("ul", {"class": "textList"})
            objs = []
            sortType = dateutil.y_m_d()
            for item in datalist:
                ahrefs = item.findAll("a")
                for ahref in ahrefs:
                    obj = {}
                    span = ahref.first('span')
                    if span != None:
                        obj['fileDate'] = span.text
                    else:
                        obj['fileDate'] = ''
                    name = ahref.text.replace(obj['fileDate'], '')
                    obj['name'] = name
                    obj['url'] = ahref.get('href')
                    obj['baseurl'] = baseurl
                    obj['channel'] = channel
                    obj['updateTime'] = datetime.datetime.now()
                    self.t_queue.put(TextItemContentParse(ahref.get('href')))
#                     txt = self.fetchText(ahref.get('href'))
#                     if txt == None:
#                         print '没有Txt文件--', ahref, '---', url
#                         continue
#                     obj['file'] = txt
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
        data = soup.first("div", {"class": "novelContent"})
        print '解析文件 ', self.t_url
        if data != None:
            obj = {}
            obj['fileUrl'] = self.t_url
            obj['file'] = data
            dbVPN = db.DbVPN()
            ops = db_ops.DbOps(dbVPN)
            ops.inertTextItems_item(obj)
            dbVPN.commit()
            dbVPN.close()
#             print url, ' 解析完成'
#             return str(data)
#         return None
