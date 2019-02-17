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

max_page = 20
list_size = 100


class ChannelParse(BaseParse):

    def __init__(self,  queue):
        threading.Thread.__init__(self)
        self.q = queue

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        try:
            objs = self.soudChannel()
            self.update(objs,ops)
            dbVPN.commit()
            dbVPN.close()
        except Exception as e:
            print common.format_exception(e)
            dbVPN.commit()
            dbVPN.close()
    def soudChannel(self):
        objs = []
        for i in range(1, 6): 
            url = "%s%s%s"%(soundUrl.replace(".html", "-"),i,".html")
            print url
            soup = self.fetchUrl(url)
            div = soup.first("div",{"class":"box movie_list"})
            if div!=None:
                for li in div.findAll("li"):
                    a = li.first("a")
                    obj = {}
                    obj['name'] = a.first('h3').text
                    obj['baseurl'] = baseurl
                    obj['url'] = a.get('href')
                    obj['updateTime'] = datetime.datetime.now()
                    obj['pic'] = a.find('img').get('data-original', "")
                    objs.append(obj)
        return objs
            
            
    def update(self, objs, ops):
        print "解析有声小说 ok----channl数=", len(objs)
        for obj in objs:
            ops.inertSoundChannel(obj)
            self.q.put(FileParse(obj, obj['url']))
        return len(objs)


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
            for i in range(1, 2):
                if i!=1:
                    url = "%s%s%s"%(self.t_obj['url'].replace(".html", "-"),i,".html")
                print url
                count = self.update(url, ops)
                dbVPN.commit()
                if count == 0:
                    break
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
        return len(objs)

    def fetchMp3(self, url):
        soup = self.fetchUrl(url)
        audio = soup.first("source")
        if audio != None:
            return audio.get('src')

        return None

    def fetchFileData(self, url, channel):
        try:
            soup = self.fetchUrl(url)
            data = soup.first("div", {"class": "text-list-html"})
            objs = []
            sortType = dateutil.y_m_d()
            if data!=None:
                item = data.first("ul")
                if item!=None:
                    ahrefs = item.findAll("a")
                    for ahref in ahrefs:
                        obj = {}
                        span = ahref.first('span')
                        if span != None:
                            obj['fileDate'] = span.text
                        else:
                            obj['fileDate'] = ''
                        name = ahref.get("title")
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
                        print name,mp3
                        obj['file'] = mp3
                        objs.append(obj)
            return objs
        except Exception as e:
            print common.format_exception(e)
