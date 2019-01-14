#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from urllib import unquote
import time
from fetch.profile import *
from urllib import unquote
import json

class VideoParse(BaseParse):

    def __init__(self):
        pass

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        chs = self.videoChannel()
        for item in chs:
            ops.inertVideoChannel(item)
        print 'dadekai video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url= item['url']
                url = "%s%s"%(url.replace(".html","-"),i)
                self.videoParse(item['channel'], url)
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        ahrefs = self.header()
        channelList = []
        for ahref in ahrefs:
            obj={}
            obj['url']=ahref.get('href')
            obj['baseurl']=baseurl
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=0.7
            obj['channel']=obj['name']=ahref.text
            obj['showType']=1
            obj['channelType']='movie'
            channelList.append(obj)
        return channelList
    def videoParse(self, channel, url):
        print url
        dataList = []
        soup = self.fetchUrl(url)
        lis  = soup.findAll("li",{"class":'p1 m1'})
        for li in lis:
            ahref = li.first('a')
            if ahref != None:
                obj = {}
                mp4Url = self.parseDomVideo(ahref.get("href"))
                if mp4Url == None:
                    print '没有mp4 文件:', ahref.get("href")
                    continue
                obj['url'] = mp4Url
                img = ahref.first("img")
                obj['pic'] = img.get("data-original")
                obj['name'] = img.get("alt")
                obj['path'] = "%s%s%s"%(channel,"-",obj['name'])
                obj['updateTime'] = datetime.datetime.now()
                if mp4Url.count("m3u8")==0:
                    obj['videoType'] = "webview"
                else:
                    obj['videoType'] = "normal"
                obj['channel'] = channel
                obj['baseurl'] = baseurl
                print obj['name'],obj['videoType'],obj['url'],obj['pic']
                dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,obj['videoType'],baseurl)

        print 'dadekai video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
      
        try:
            vedioId = url.replace("/html/","").replace(".html","")
            url = "/play/%s-1-1.html"%(vedioId)
            soup = self.fetchUrl(url)
            div = soup.first("div",{"class":"player mb"})
            if div!=None:
                script = div.first("script")
                if script!=None:
                    content = unquote(str(script.text)).replace("var player_data=", "")
                    obj = json.loads(content)
                    if obj!=None:
                        return obj.get("url",None)
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
