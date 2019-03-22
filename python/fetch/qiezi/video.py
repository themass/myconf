#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common, httputil
from urllib import unquote
import time
from fetch.profile import *
from baseparse import baseurl
import json

class VideoParse(BaseParse):

    def __init__(self):
        pass

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        chs  = self.videoChannel()
        for ch in chs:
            ops.inertVideoChannel(ch)
        print ' channel ok; len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for ch in chs:
            for i in range(60, maxVideoPage):
                url= ch['url']
                self.videoParse(ch['channel'],url, i)
                print '解析完成 ', ch['channel'], ' ---', i, '页'
    def videoChannel(self):
        channelList = []
        obj={}
        obj['name']='茄子视频'
        obj['url']='/api/query/getQuery'
        obj['baseurl']=baseurl
        obj['updateTime']=datetime.datetime.now()
        obj['pic']=''
        obj['rate']=1.2
        obj['channel']=obj['name']
        obj['showType']=3
        obj['channelType']='normal'
        channelList.append(obj)
        return  channelList
    def videoParse(self, channel, url,i):
        dataList = []
        para = {}
        para['method']='created_at'
        para['order']='desc'
        para['step']=i
        obj = httputil.getData(baseurl+url,para,header)
        for item in obj['data']['videos']:
            mp4Url  = item.get("url")
            if mp4Url==None:
                continue
            obj = {}
            obj['url'] = "http://qiezsp889911.chuantouchi.com:8092"+mp4Url
            obj['pic'] = item.get("horizontal_cover")
            obj['name'] = item.get("video_name")
            obj['path'] = "qinzi%s"%(mp4Url)
            obj['videoType'] = "normal"
            print obj['videoType'],obj['name'],mp4Url,obj['pic']
            obj['updateTime'] = datetime.datetime.now()
            obj['channel'] = channel
            obj['baseurl'] = baseurl
            dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,obj['videoType'],baseurl)

        print 'f8dy video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
