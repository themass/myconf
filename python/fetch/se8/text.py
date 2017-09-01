#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import threading
from common.envmod import *
from common import common
from common import db_ops
from baseparse import *
global baseurl


class TextChannelParse(BaseParse):

    def __init__(self, obj):
        threading.Thread.__init__(self)
        self.t_obj = obj

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
                for i in range(1, 500):
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
            ops.inertTextFile(obj)
        return len(objs)

    def fetchTextData(self, url, channel):
        try:
            soup = self.fetchUrl(url)
            datalist = soup.findAll("ul", {"class": "textList"})
            objs = []
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
                    txt = self.fetchText(ahref.get('href'))
                    if txt == None:
                        print '没有Txt文件--', ahref, '---', url
                        continue
                    obj['file'] = txt
                    objs.append(obj)
            return objs
        except Exception as e:
            print common.format_exception(e)

    def fetchText(self, url):
        soup = self.fetchUrl(url)
        data = soup.first("div", {"class": "novelContent"})
        if data != None:
            print url, ' 解析完成'
            return str(data)
        return None
