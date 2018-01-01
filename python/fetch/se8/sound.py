#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import threading
from common import common
from common import dateutil
from baseparse import *
from common import db_ops
from common.envmod import *
global baseurl

max_page = 10
list_size = 10


class ChannelParse(BaseParse):

    def __init__(self, obj, queue):
        threading.Thread.__init__(self)
        self.t_obj = obj
        self.q = queue

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        try:
            url = self.t_obj['url']
            first = self.parsFirstPage(url)
            print first
            if first != None:
                for i in range(1, max_page):
                    url = first + str(i) + ".htm"
                    count = self.update(url, ops)
                    dbVPN.commit()
                    if count == 0:
                        break
            else:
                self.update(url, ops)
                dbVPN.commit()
            dbVPN.close()
        except Exception as e:
            print common.format_exception(e)
            dbVPN.commit()
            dbVPN.close()

    def update(self, url, ops):
        lis = self.fetchDataHead(url)
        objs = self.parsDataText(lis)
        print "解析有声小说 ok----channl数=", len(objs)
        for obj in objs:
            ops.inertSoundChannel(obj)
            self.q.put(FileParse(obj, obj['url']))
        return len(objs)

    def fetchDataHead(self, url):
        try:
            soup = self.fetchUrl(url)
            lis = soup.findAll("li")
            return lis

        except Exception as e:
            print common.format_exception(e)

    def parsDataText(self, lis):
        objs = []
        for li in lis:
            a = li.first("a")
            obj = {}
            obj['name'] = a.first('h3').TEXT
            obj['baseurl'] = baseurl
            obj['url'] = a.get('href')
            obj['updateTime'] = datetime.datetime.now()
            obj['pic'] = a.find('img').get('src', "")
            objs.append(obj)
        return objs


class FileParse(BaseParse):

    def __init__(self, obj, channel):
        threading.Thread.__init__(self)
        self.t_obj = obj
        self.t_channel = channel

    def run(self):
        print '解析列表页 channel：', self.t_channel
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        try:
            url = self.t_obj['url']
            first = self.parsFirstPage(url)
            print '分页', first
            if first != None:
                for i in range(1, list_size):
                    url = first + str(i) + ".htm"
                    count = self.update(url, ops)
                    dbVPN.commit()
                    if count == 0:
                        break
            else:
                self.update(url, ops)
                dbVPN.commit()
            dbVPN.close()
        except Exception as e:
            print common.format_exception(e)
            dbVPN.commit()
            dbVPN.close()

    def update(self, url, ops):
        objs = self.fetchFileData(url, self.t_channel)
        print threading.current_thread().getName(), "解析有声小说  mp3 ok----数据items=", len(objs), '--channel:', self.t_channel
        for obj in objs:
            ret = ops.inertSoundItems(obj)
            if ret == None:
                return 0
        return len(objs)

    def fetchMp3(self, url):
        soup = self.fetchUrl(url)
        audio = soup.find("audio")
        if audio != None:
            return audio.get('src')

        return None

    def fetchFileData(self, url, channel):
        try:
            soup = self.fetchUrl(url)
            datalist = soup.findAll("div", {"class": "box list channel"})
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
                    obj['sortType'] = sortType
                    mp3 = self.fetchMp3(ahref.get('href'))
                    if mp3 == None:
                        print '没有mp3文件--', ahref, '---', url
                        continue
                    obj['file'] = mp3
                    objs.append(obj)
            return objs
        except Exception as e:
            print common.format_exception(e)
