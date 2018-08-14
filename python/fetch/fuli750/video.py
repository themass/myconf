#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common, httputil
from urllib import unquote
import time
from fetch.profile import *

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
            for i in range(225, maxVideoPage):
                url= ch['url']
                if i!=1:
                    url= "%s%s%s"%(ch['url'],"?page=",i)
                self.videoParse(ch['channel'], url)
                print '解析完成 ', ch['channel'], ' ---', i, '页'
    def videoChannel(self):
        objs = []
        obj = {}
        obj['name']="fuli750"
        obj['url']="/video/lists"
        obj['baseurl']=baseurl
        obj['updateTime']=datetime.datetime.now()
        obj['pic']=''
        obj['rate']=1.2
        obj['channel']='fuli750'+obj['url']
        obj['showType']=3
        obj['channelType']='normal'
        objs.append(obj)
        return  objs
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        div = soup.first("ul", {"class": "panel"})
        if div!=None:
            lis = div.findAll('li',{"class":"sort-cel"})
            for li in lis:
                ahref = li.first('a')
                if ahref!=None:
                    mp4Url  = self.parseDomVideo(ahref.get("href"))
                    if mp4Url==None:
                        continue
                    obj = {}
                    obj['url'] = mp4Url
                    img = ahref.first("img")
                    obj['pic'] = img.get('src')
                    obj['name'] = li.first('li',{"class":"title"}).text
                    print obj['name'],mp4Url,obj['pic']
    
                    videourl = urlparse(obj['url'])
                    obj['path'] = videourl.path
                    obj['updateTime'] = datetime.datetime.now()
                    obj['channel'] = channel
                    obj['baseurl'] = baseurl
                    dataList.append(obj)
            dbVPN = db.DbVPN()
            ops = db_ops.DbOps(dbVPN)
            for obj in dataList:
                ops.inertVideo(obj,"normal",baseurl)
    
            print 'fuli750 video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
            dbVPN.commit()
            dbVPN.close()

    def parseDomVideo(self, url):
        try:
            match = videoId.search(url)
            if match!=None:
                data = {}
                data['id']=match.group(1)
                ret = httputil.postRequestWithParam(videoGet, data, header)
                mp4 = ret.get("data",{}).get("videoInfo",{}).get("url",None)
                if mp4==None:
                    print url,'没有mp4',ret
                    return None
                return mp4
            print url,'没有mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
