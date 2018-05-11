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
        print 'miaobosp video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, 2):
                url= item['url']
                self.videoParse(item['channel'], url)
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        channelList =[]
        obj={}
        obj['url']="/?m=vod-type-id-19.html"
        obj['baseurl']=baseurl
        obj['updateTime']=datetime.datetime.now()
        obj['pic']='http://img.wopare.com/vod/t4m2xvm0nfk.jpg'
        obj['rate']=0.7
        obj['channel']=obj['name']="推女精短"
        obj['showType']=3
        obj['channelType']='movie'
        channelList.append(obj)
        return channelList
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        lis = soup.findAll("li",{"class":'p1 m1 '})
        for li in lis:
            ahref = li.first('a')
            if ahref != None:
                namep = ahref.get("title")
                img = ahref.first("img")
                pic =img.get("src")
                
                soup = self.fetchUrl(ahref.get("href"))
                div = soup.first("div",{"class":"playlist clearfix"})
                if div!=None:
                    aji = div.first("a")
                    mp4Urls = self.parseDomVideo(aji.get("href"))
                    index =1
                    for mp4Url in mp4Urls:
                        if mp4Url == None:
                            print '没有mp'
                            continue
                        obj = {}
                        obj['url'] = mp4Url
                        obj['pic'] = pic
                        obj['name'] = "%s-%s"%(namep,index)
                        obj['path'] = "%s%s%s"%(channel,"-",obj['name'])
                        obj['updateTime'] = datetime.datetime.now()
                        if mp4Url.count("m3u8")==0 and mp4Url.count("mp4")==0:
                            obj['videoType'] = "webview"
                        else:
                            obj['videoType'] = "normal"
                        obj['channel'] = channel
                        obj['baseurl'] = baseurl
                        print obj['videoType'],obj['url'],obj['pic']
                        dataList.append(obj)
                        index = index+1
                        
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,obj['videoType'],baseurl)

        print 'miaobosp video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
      
        try:
            urls = []
            soup = self.fetchUrl(url)
            div = soup.first("div",{"class":"player mb"})
            if div!=None:
                script = div.first("script")
                if script!=None:
                    content = unquote(str(script.text)).replace("#", "$").split("$")
                    for item in content:
                        match = regVideo.search(item)
                        if match!=None: 
                            urls.append("http"+match.group(1)+'mp4')
            return urls
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
