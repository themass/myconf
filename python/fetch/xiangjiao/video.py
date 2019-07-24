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
            for i in range(1, maxVideoPage):
                url= "%s%s"%(ch['url'],i)
                self.videoParse(ch['channel'],url)
                print '解析完成 ', ch['channel'], ' ---', i, '页'
    def videoChannel(self):
        channelList = []
        for item in channels:
            obj={}
            obj['name']='香蕉视频'
            obj['baseurl']=baseurl
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1.2
            obj['channel']=obj['name']
            obj['showType']=3
            obj['channelType']='normal'
            obj['url']=item
            channelList.append(obj)
        return  channelList
    def videoParse(self, channel, url):
        dataList = []
        obj = httputil.getData(baseurl+url,{},header)
        if obj==None or obj.get('data',None)==None or obj.get('data',None).get('vodrows',None)==None:
            return 
        for item in obj['data']['vodrows']:
            mp4Url  = self.getMp4(item.get("play_url"))
            if mp4Url==None:
                continue
            obj = {}
            obj['url'] = mp4Url
            obj['pic'] =item.get("coverpic")
            obj['name'] = item.get("title",'')
            obj['path'] = "xij%s"%(mp4Url)
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
        time.sleep(2)
    def getMp4(self,url):
        print url
        obj = httputil.getData(baseurl+url,{},header)
        if obj==None or obj.get('data',{})==None:
            return None
        if  obj.get('data',{}).get('httpurl',None)!=None:
            return obj['data']['httpurl']
        if  obj.get('data',{}).get('httpurl_preview',None)!=None:
            return obj['data']['httpurl_preview']
        return None