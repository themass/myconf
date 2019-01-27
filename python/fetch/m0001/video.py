#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from urllib import unquote
import time
from fetch.profile import *
class VideoUserParse(BaseParse):

    def __init__(self):
        pass

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        chs = self.videoChannel()
        for item in chs:
            ops.inertVideoUser(item)
        print 'm0001 user video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url = item['url']
                url= "%s%s%s"%(item['url'].replace(".html","-pg-"),i,".html")
                print url
                self.videoParse(item['channel'], url,item['userId'])
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        ahrefs = self.header()
        channelList = []
        for ahref in ahrefs:
            obj={}
            obj['name']=ahref.text
            obj['url']=ahref.get('href')
            obj['baseUrl']=baseurl
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1.2
            obj['channel']='m0001_all'
            obj['userId']="m0001_"+ahref.text
            obj['showType']=3
            channelList.append(obj)
        return channelList
    def videoParse(self, channel, url,userId):
        dataList = []
        soup = self.fetchUrl(url)
        div = soup.first("div", {"class": "box movie_list"})
        if div!=None:
            metas = div.findAll("li")
            for meta in metas:
                obj = {}
                ahref = meta.first("a")
                mp4Url = self.parseDomVideo(ahref.get("href"))
                if mp4Url == None:
                    print '没有mp4 文件:', ahref.get("href")
                    continue
                obj['url'] = mp4Url
                obj['pic'] = meta.first('img').get("src")
                obj['name'] = meta.first('h3').text
    
                videourl = urlparse(obj['url'])
                obj['path'] = 'm0001_'+videourl.path
                obj['updateTime'] = datetime.datetime.now()
                obj['channel'] = channel
                if mp4Url.count("m3u8")==0 and mp4Url.count("mp4")==0:
                    obj['videoType'] = "webview"
                else:
                    obj['videoType'] = "normal"
                obj['baseUrl'] = baseurl
                obj['rate'] = 1.2
                obj['userId'] = userId
                obj['showType'] = 3
                print obj['name'],obj['videoType'],obj['url'],obj['pic']
                
                dataList.append(obj)
                
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideoUserItem(obj)

        print 'mm7 video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
        try:
            url = url.replace("/?m=vod-detail-id-","").replace(".html","")
            url = "%s%s%s"%("/?m=vod-play-id-",url,"-src-1-num-1.html")
            soup = self.fetchUrl(url, header)
            text = soup.first("div",{"class":"player_l"})
            text = unquote(text)
            texts = text.split(",")
            for item in texts:
                match = regVideo.search(item)
                if match!=None:
                    return "%s%s%s"%("http",match.group(1),"m3u8")
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

