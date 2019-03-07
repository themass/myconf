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
        print 'baseurl12 user video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url= item['url']
                url = "%s%s%s"%(item['url'],base_videourl,i)
                print url
                self.videoParse(item['channel'], url,item['userId'])
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        ahrefs = self.headers("header13.html")
        channelList = []
        print len(ahrefs)
        for ahref in ahrefs:
            obj={}
            obj['name']=ahref.get("title")
            obj['url']=ahref.get('href')
            obj['baseUrl']=baseurl13
            obj['updateTime']=datetime.datetime.now()
            img = ''
            if ahref.first("img")!=None:
                img = ahref.first("img").get("src")
            obj['pic']=img
            obj['rate']=1.2
            obj['channel']='蝌蚪窝3'
            obj['userId']="蝌蚪窝3"+ahref.get("title")
            obj['showType']=3
            obj['channelType']='normal'
            channelList.append(obj)
        return channelList
    def videoParse(self, channel, url,userId):
        dataList = []
        soup = self.fetchUrl(url,header8)
        lis = soup.findAll("div",{"class":"item  "})
        for li in lis:
            ahref = li.first("a")
            obj = {}
            mp4Url = self.parseDomVideo(ahref.get("href"))
            if mp4Url == None:
                print '没有mp4 文件:', ahref.get("href")
                continue
            obj['url'] = mp4Url
            img = li.first("img")
            obj['pic'] = img.get("data-original")
            obj['name'] = ahref.get("title")

            videourl = urlparse(obj['url'])
            obj['path'] = "caca049"+videourl.path
            obj['rate'] = 1.2
            obj['updateTime'] = datetime.datetime.now() 
            obj['userId'] = userId
            obj['baseUrl'] = baseurl13 
            obj['showType'] = 3
            obj['videoType'] = "webview"
            print obj['videoType'],obj['name'],mp4Url,obj['pic']
            dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideoUserItem(obj)

        print 'base13 video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
    def parseDomVideo(self, url):
        try:
            url = url.replace(baseurl13,"").replace("/videos/","")
            ids = url.split("/")
            return "https://kkembed.kdwembed.com/embed/"+ids[0]
        except Exception as e:
            print common.format_exception(e)
            return None

