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
                url= ch['url']
                count = self.videoParse(ch['channel'],url, i,None)
                if count==0:
                    break
                print '解析完成 ', ch['channel'], ' ---', i, '页'
    def videoChannel(self):
        channelList = []
        obj={}
        obj['name']='抖音源库'
        obj['url']='/api/public/?service=Video.getRecommendVideos&uid=-1&p='
        obj['baseurl']=baseurl
        obj['updateTime']=datetime.datetime.now()
        obj['pic']=''
        obj['rate']=1.2
        obj['channel']=obj['name']
        obj['showType']=3
        obj['channelType']='normal'
        channelList.append(obj)
        
        obj={}
        obj['name']='抖音源库'
        obj['url']='/api/public/?service=Video.getVideoList&uid=-1&p='
        obj['baseurl']=baseurl
        obj['updateTime']=datetime.datetime.now()
        obj['pic']=''
        obj['rate']=1.2
        obj['channel']=obj['name']
        obj['showType']=3
        obj['channelType']='normal'
        channelList.append(obj)
        return  channelList
    def videoParse(self, channel, url,i,key):
        dataList = []
        para = {}
        url = baseurl+url+str(i)
        print url
        obj = httputil.getData(url,para,header)
        for item in obj.get('data',{}).get('info',[]):
            mp4Url  = item.get("href")
            if mp4Url==None:
                continue
            obj = {}
            obj['url'] = mp4Url
            obj['pic'] = item.get("thumb")
            obj['name'] = item.get("title",'')
            obj['path'] = "f2d%s"%(mp4Url)
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
        return len(obj.get('data',{}).get('info',[]))
   