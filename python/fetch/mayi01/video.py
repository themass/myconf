#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from urllib import unquote
import time
from fetch.profile import *
class VideoUserParse(BaseParse):

# http://sexbee1.top//getToken.php 
#update video_user_item set url = replace(url,"?sign=f3d7823eba0ab084f41cb71b8debb3e9web","?sign=f3d7823eba0ab084f41cb71b8debb3e9") where baseurl = "http://sexbee1.top/"
    def __init__(self):
        pass

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        chs = self.videoChannel()
        for item in chs:
            ops.inertVideoUser(item)
        print 'sexbee1 user video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url= item['url']
                if i!=1:
                    url= "%s%s%s"%(item['url'].replace("0.html",""),i,".html")
                print url
                self.videoParse(item['channel'], url,item['userId'])
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        ahrefs = self.header("header2.html")
        channelList = []
        for ahref in ahrefs:
            obj={}
            obj['name']=ahref.text
            obj['url']=ahref.get('href')
            obj['baseurl']=baseurlVideo
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1.2
            obj['channel']='蜜蜂资源'
            obj['userId']=ahref.text
            obj['showType']=3
            obj['channelType']='normal'
            channelList.append(obj)
        return channelList
    def videoParse(self, channel, url,userId):
        dataList = []
        soup = self.fetchUrl(baseurlVideo+url)
        div = soup.first("div", {"class": "threadList"})
        if div!=None:
            lis = div.findAll("a")
            for item in lis:
                obj = {}
                mp4Url = self.parseDomVideo(item.get("href"))
                if mp4Url == None:
                    print '没有mp4 文件:', item.get("href")
                    continue
                obj['url'] = mp4Url
                img = item.first("img")
                obj['pic'] = img.get("data-original")
                 
                name = item.first('div',{"class":"text"}).text
                names = name.split("月")
                obj['name'] = names[0]
                videourl = urlparse(obj['url'])
                obj['path'] = "sexbee1"+videourl.path
                obj['rate'] = 1.2
                obj['updateTime'] = datetime.datetime.now()
                obj['userId'] = userId
                obj['baseUrl'] = baseurlVideo
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

        print 'ppyy55 video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
        try:
            soup = self.fetchUrl(baseurlVideo+url)
            adiv = soup.first("input",{"class":"videoUrl"})
            if adiv!=None:
                return adiv.get("value")
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

