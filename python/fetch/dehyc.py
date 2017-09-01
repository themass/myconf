#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import urllib2
import threading
from BeautifulSoup import BeautifulSoup
from common.envmod import *
from common import common
from common import typeutil
from common import db_ops
from common import MyQueue
from common import httputil
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')
# http://www.dehyc.com
baseurl = "http://www.dehyc.com"
baseurl_text = 'http://58.84.54.38:8010'
queue = MyQueue.MyQueue(20000)
maxCount = 5
soundUrl = '/api/dirlist.ashx'
soundItemUrl = '/api/mp3data.ashx'
textchannelUrl = '/api/category.ashx'
textItemUrl = '/api/bookdata.ashx'
textFileUrl = '/api/bookdata.ashx'
header = {'User-Agent': 'okhttp/3.3.1'}


class HandleThread(threading.Thread):

    def __init__(self, name, queue):
        threading.Thread.__init__(self, name=name)
        self.t_name = name
        self.t_queue = queue

    def run(self):
        while(True):
            try:
                print queue.qsize()
                obj = queue.get(timeout=30)
                obj.run()
            except Exception as e:
                print threading.current_thread().getName(), '---conti'
                pass


class SoundItemParse(threading.Thread):

    def __init__(self, obj):
        self.t_obj = obj

    def run(self):
        param = {}
        param['action'] = 'mp3list'
        param['pagesize'] = 1000
        param['pageindex'] = 1
        param['dirid'] = self.t_obj.get('dir')
        data = httputil.postRequestWithParam(
            baseurl + soundItemUrl, param, header)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        ret = data.get('data', [])
        for item in ret:
            obj = {}
            obj['fileDate'] = ''
            obj['name'] = item.get('mp3_title', '')
            obj['url'] = soundItemUrl
            obj['baseurl'] = baseurl
            obj['channel'] = self.t_obj.get('url')
            obj['updateTime'] = datetime.datetime.now()
            obj['file'] = item.get('mp3_url', '')
            ops.inertSoundFile(obj)
        print 'dehyc channel=', self.t_obj['url'], '--解析完毕'
        dbVPN.commit()
        dbVPN.close()


def SoundParse():
    param = {}
    param['action'] = 'dirlist'
    param['pagesize'] = 1000
    param['pageindex'] = 1
    param['type'] = 0
    data = httputil.postRequestWithParam(baseurl + soundUrl, param, header)
    ret = data.get('data', [])
    objs = []
    if len(ret) > 0:
        for item in ret:
            obj = {}
            obj['name'] = item.get('dir_title', '性福之事')
            obj['baseurl'] = baseurl
            obj['url'] = soundUrl + '/' + str(item.get('dir_id', 0))
            obj['dir'] = item.get('dir_id', 0)
            obj['updateTime'] = datetime.datetime.now()
            obj['pic'] = item.get('dir_img_url', '')
            queue.put(SoundItemParse(obj))
            objs.append(obj)
            print 'dehyc channel=', obj['url'], '--加入队列'
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in objs:
            ops.inertSoundChannel(obj)
        print 'dehyc 更新channel ok ', len(objs)
        dbVPN.commit()
        dbVPN.close()


class TextItemsParse(threading.Thread):

    def __init__(self, obj, page):
        self.t_obj = obj
        self.t_page = page

    def run(self):
        param = {}
        param['action'] = 'list'
        param['pagesize'] = 10
        param['pageindex'] = self.t_page
        param['type'] = self.t_obj.get('dir')
        data = httputil.postRequestWithParam(
            baseurl_text + textItemUrl, param, header)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        ret = data.get('data', [])
        for item in ret:
            obj = {}
            obj['fileDate'] = ''
            obj['name'] = item.get('title', '')
            obj['url'] = textFileUrl + '/' + str(item.get('id', 0))
            obj['baseurl'] = baseurl_text
            obj['channel'] = self.t_obj.get('url')
            obj['updateTime'] = datetime.datetime.now()
            obj['file'] = self.parseText(item.get('id', 0))
            ops.inertTextFile(obj)
        print 'dehyc channel=', self.t_obj['url'], '--解析完毕---', self.t_page, 'size=', len(ret)
        dbVPN.commit()
        dbVPN.close()

    def parseText(self, id):
        param = {}
        param['action'] = 'bookfile'
        param['id'] = id
        data = httputil.getTextByRequst(
            baseurl_text + textFileUrl, param, header)
        return data


def textParse():
    param = {}
    param['action'] = 'list'
    param['pid'] = 0
    data = httputil.postRequestWithParam(
        baseurl_text + textchannelUrl, param, header)
    ret = data.get('data', [])
    objs = []
    if len(ret) > 0:
        for item in ret:
            obj = {}
            obj['name'] = item.get('title', '性福之事') + "2"
            obj['baseurl'] = baseurl_text
            obj['url'] = textchannelUrl + '/' + str(item.get('id', 0))
            obj['dir'] = item.get('id', 0)
            obj['updateTime'] = datetime.datetime.now()
            for i in range(1, 50):
                queue.put(TextItemsParse(obj, i))
            objs.append(obj)
            print 'dehyc text channel=', obj['url'], '--加入队列'
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in objs:
            ops.inertTextChannel(obj)
        print 'dehyc text 更新channel ok ', len(objs)
        dbVPN.commit()
        dbVPN.close()

if __name__ == '__main__':

    for i in range(0, 30):
        worker = HandleThread("work-%s" % (i), queue)
        worker.start()
#     SoundParse()
    textParse()
