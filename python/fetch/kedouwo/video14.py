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
        print '隔壁老王 user video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url= item['url']
                url = item['url'].replace("-pg-1","-pg-"+str(i))
                print url
                self.videoParse(item['channel'], url,item['userId'])
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        ahrefs = self.headers("header14.html")
        channelList = []
        for ahref in ahrefs:
            obj={}
            obj['name']=ahref.text
            obj['url']=ahref.get('href')
            obj['baseurl']=baseurl14
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1.2
            obj['channel']='隔壁老王'
            obj['userId']="隔壁老王"+ahref.text
            obj['showType']=3
            obj['channelType']='normal'
            channelList.append(obj)
        return channelList
    def videoParse(self, channel, url,userId):
        dataList = []
        soup = self.fetchUrl(baseurl14+url,header8)
        div = soup.first("div",{"class":"box movie_list"})
        if div!=None:
            lis = div.findAll("li")
            for li in lis:
                ahref = li.first("a")
                obj = {}
                mp4Url = self.parseDomVideo(ahref.get("href"))
                if mp4Url == None:
                    print '没有mp4 文件:', ahref.get("href")
                    continue
                obj['url'] = mp4Url
                img = li.first("img")
                obj['pic'] = img.get("src")
                obj['name'] = ahref.get("title")
    
                videourl = urlparse(obj['url'])
                obj['path'] = "gebi0"+videourl.path
                obj['rate'] = 1.2
                obj['updateTime'] = datetime.datetime.now() 
                obj['userId'] = userId
                obj['baseUrl'] = baseurl14
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

        print '91gc video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
    def parseDomVideo(self, url):
        try:
            url = url.replace("/vod-detail-id-","").replace(".html","")
            url = "%s%s%s"%("/vod-play-id-",url,"-src-1-num-1.html")
            soup = self.fetchUrl(baseurl14+url, header)
            div   = soup.first("div",{"class":"box pic_text"})
            if div !=None:
                text = unquote(unquote(str(div.text)))
                texts = text.split("$")
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

