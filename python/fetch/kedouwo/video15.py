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
        print 'qiezi user video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url= item['url']
                url = "%s%s%s"%(item['url'].replace(".html","/page/"),i,".html")
                self.videoParse(item['channel'], url,item['userId'])
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        ahrefs = self.headers("header15.html")
        channelList = []
        for ahref in ahrefs:
            obj={}
            obj['name']=ahref.text
            obj['url']=ahref.get('href')
            obj['baseurl']=baseurl15
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1.2
            obj['channel']='茄子视频'
            obj['userId']="茄子视频"+ahref.text
            obj['showType']=3
            obj['channelType']='normal'
            channelList.append(obj)
        return channelList
    def videoParse(self, channel, url,userId):
        dataList = []
        soup = self.fetchUrl(baseurl15+url,header14)
        div = soup.first("ul",{"class":"videos"})
        if div!=None:
            lis = div.findAll("div",{"class":"video"})
            for li in lis:
                ahref = li.first("a")
                obj = {}
                mp4Url = self.parseDomVideo(ahref.get("href"))
                if mp4Url == None:
                    print '没有mp4 文件:', ahref.get("href")
                    continue
                obj['url'] = mp4Url
                img = li.first("img")
                obj['pic'] = baseurl15+img.get("src")
                obj['name'] = img.get("alt")
    
                videourl = urlparse(obj['url'])
                obj['path'] = "qzi2"+videourl.path
                obj['rate'] = 1.2
                obj['updateTime'] = datetime.datetime.now() 
                obj['userId'] = userId
                obj['baseUrl'] = baseurl15
                obj['showType'] = 3
                if mp4Url.count("m3u8")==0 and mp4Url.count("mp4")==0:
                    obj['videoType'] = "webview"
                else:
                    obj['videoType'] = "normal"
                print obj['videoType'],obj['name'],mp4Url,obj['pic']
                dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideoUserItem(obj)

        print 'qzi2 video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
    def parseDomVideo(self, url):
        try:
            soup = self.fetchUrl(baseurl15+url, header14)
            div   = soup.first("div",{"id":"bofang_box"})
            if div !=None:
                text = unquote(unquote(str(div.text)))
                texts = text.split(",")
                for item in texts:
                    match = regVideoM3.search(item)
                    if match!=None:
                        videoUrl =match.group(1).replace("\/","/").replace("*屏蔽的关键字*","xxx")
                        return "%s%s%s"%("http",videoUrl,'m3u8')
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

