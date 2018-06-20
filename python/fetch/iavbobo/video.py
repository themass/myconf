#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from urllib import unquote
import time
from fetch.profile import *
from urllib import unquote

class VideoParse(BaseParse):

    def __init__(self):
        pass

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        chs = self.videoChannel()
        for item in chs:
            ops.inertVideoChannel(item)
        print 'iavbobo video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                page = '%s%s'%("page=",i)
                url= item['url'].replace("page=1",page)
                self.videoParse(item['channel'], url)
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        channelList =[]
        obj={}
        obj['url']='/search?keyword=&page=1&limit=10'
        obj['baseurl']=baseurl
        obj['updateTime']=datetime.datetime.now()
        obj['pic']=''
        obj['name']='爱波波'
        obj['rate']=1
        obj['channel']='iavbobo'
        obj['showType']=3
        obj['channelType']='normal'
        channelList.append(obj)
        return channelList
    def videoParse(self, channel, url):
        dataList = []
        data = self.fetchUrl(url)
        docs = data.get("docs",[])
        for item in docs:
            obj = {}
            lowHls = item.get("low-hls")
            mp4Url = None
            if lowHls!=None and lowHls!='':
                mp4Url = lowHls.replace("http://ss2.999cdn.us","http://cdn.viparts.net/src2").replace("http://sss.999cdn.us","http://cdn.viparts.net/src2")
            else:
                source = item.get("sources_me",{})
                for key,val in source.items():
                    mp4Url = val.replace("http://ss2.999cdn.us","http://cdn.viparts.net/src2").replace("http://sss.999cdn.us","http://cdn.viparts.net/src2")
            if mp4Url == None:
                print '没有mp4 文件:',item['id']
                continue
            obj['url'] = mp4Url
            obj['pic'] = item.get("cover_full")
            obj['name'] = item.get("title")
            videourl = urlparse(obj['url'])
            obj['path'] = "iavbobo"+videourl.path
            obj['updateTime'] = datetime.datetime.now()
            if mp4Url.count("m3u8")==0 and mp4Url.count("mp4")==0:
                obj['videoType'] = "webview"
            else:
                obj['videoType'] = "normal"
            obj['channel'] = channel
            obj['baseurl'] = baseurl
            print obj['url'],obj['pic']
            dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,obj['videoType'],baseurl)

        print 'iavbobo video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
      
        try:
            soup = self.fetchUrl(url)
            div = soup.first("div",{"class":"videourl"})
            if div!=None:
                ahref = div.first("a")
                if ahref!=None:
                    soup = self.fetchUrl(ahref.get("href"))
                    player = soup.first("div",{"class":"player"})
                    if player!=None:
                        script = player.first("script")
                        if script!=None:
                            content = unquote(str(script.text)).split("$")
                            for item in content:
                                match = regVideo.search(item)
                                if match!=None: 
                                    return "http"+match.group(1)+'m3u8'
                                elif item.count(regVideoYun)>0:
                                    return item
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
