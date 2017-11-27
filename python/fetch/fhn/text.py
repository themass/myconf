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
            prefixUrl = url.replace("index.html", "")
            print first, url

            # 第一页
            url = prefixUrl + "index.html"
            self.update(url, ops, channel)
            dbVPN.commit()
            if first != None:
                for i in range(2, maxTextChannelPage):
                    url = prefixUrl + "index_" + str(i) + ".html"
                    count = self.update(url, ops, channel)
                    dbVPN.commit()
                    if count == 0:
                        break
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
            div = soup.first("div", {"class": "artlist"})
            if div == None:
                print '没有数据', url
                return []
            datalist = div.findAll("li")
            objs = []
            sortType = dateutil.y_m_d()
            for item in datalist:
                ahref = item.first("a")
                obj = {}
                span = item.first('span')
                if span != None:
                    obj['fileDate'] = span.text
                else:
                    obj['fileDate'] = ''
                name = ahref.text
                obj['name'] = name
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
        prefixUrl = self.t_url.replace(".html", "")
        url = prefixUrl + ".html"
        # 第一页
        data = self.pageTextData(url)
        first = self.parsFirstPage(self.t_url)
        print '解析文件 ', self.t_url, 'first=', first
        if first != None:
            for i in range(2, 10):
                url = prefixUrl + "_" + str(i) + ".html"
                content = self.pageTextData(url)
                if content == '':
                    break
                data = data + content
        try:
            obj = {}
            obj['fileUrl'] = self.t_url
            obj['file'] = data
            dbVPN = db.DbVPN()
            ops = db_ops.DbOps(dbVPN)
            ops.inertTextItems_item(obj)
            dbVPN.commit()
            dbVPN.close()
        except Exception as e:
            print common.format_exception(e)
#             print url, ' 解析完成'
#             return str(data)
#         return None

    def pageTextData(self, url):
        soup = self.fetchUrl(url)
        data = soup.first("div", {"class": "artbody imgbody"})
        if data == None:
            return ''
        data = str(data)
        data = self.removePage(data)
        return data
