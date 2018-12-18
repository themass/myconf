#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from urllib import unquote
import time

from fetch.profile import *
class VideoParse(BaseParse):

    def __init__(self):
        pass

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        chs = self.videoChannel()
        for item in chs:
            ops.inertVideoChannelLine(item)
        print 'newlynet video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url = item['url']
                if i!=1:
                    url= "%s%s%s%s"%(item['url'],"page_",i,".html")
                print url
                self.videoParse(item['channel'], url,item['baseurl'])
                print '解析完成 ', item['baseurl'],item['channel'], ' ---', i, '页'
    def videoChannel(self):
        channelList = []
        obj={}
        obj['name']="番号大全"
        obj['url']=pageurl
        obj['baseurl']=baseurl
        obj['updateTime']=datetime.datetime.now()
        obj['pic']=''
        obj['rate']=1
        obj['channel']='newlynet'
        obj['showType']=3
        obj['channelType']='newlynet_all'
        channelList.append(obj)
        channelList.reverse()
        return channelList
    def videoParse(self, channel, url,base):
        dataList = []
        soup = self.fetchUrl(url,header)
        metas = soup.findAll("div",{"class":"news"})
        for item in metas:
            ahref = item.first("a")
            if ahref !=None:
                mp4Urls  = self.parseDomVideo(base,ahref.get("href"))
                for mp4Url in mp4Urls:
                    obj = {}
                    obj['url'] = mp4Url['url']
                    obj['pic'] = baseurl+ahref.first('img').get("data-original")
                    obj['name'] = mp4Url['name']
        
                    obj['path'] = 'newlynet_'+mp4Url['url'][-10:]
                    obj['updateTime'] = datetime.datetime.now()
                    obj['channel'] = channel
                    obj['videoType'] = "normal"
                    obj['baseurl'] = baseurl
                    print obj['name'],obj['videoType'],obj['url'],obj['pic']
                    dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideoLine(obj,obj['videoType'],baseurl)

        print '36kpd  video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, base,url):
        try:
            soup = self.fetchUrl(url, header)
            divs = soup.findAll("div")
            urls = []
            for div in divs:
                ahref = div.first("a")
                divTitle = div.first("div")
                if ahref!=None and divTitle!=None and ahref.get("rel")!=None:
                    obj = {}
                    obj['name']=divTitle.text
                    obj['url']=ahref.get("href")
                    urls.append(obj)
            
            return urls
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
