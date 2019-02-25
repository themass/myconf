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
        print 'aotu user video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url= item['url']
                url = "%s%s%s"%(item['url'].replace(".html","/page/"),i,".html")
                print url
                self.videoParse(item['channel'], url,item['userId'])
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        ahrefs = self.header9()
        channelList = []
        for ahref in ahrefs:
            obj={}
            obj['name']=ahref.text
            obj['url']=ahref.get('href')
            obj['baseurl']=baseurl9
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1.2
            obj['channel']='91国产影院'
            obj['userId']="91国产"+ahref.text
            obj['showType']=3
            obj['channelType']='normal'
            channelList.append(obj)
        return channelList
    def videoParse(self, channel, url,userId):
        dataList = []
        soup = self.fetchUrl(baseurl9+url,header8)
        lis = soup.findAll("li",{"class":"col-md-6 col-sm-4 col-xs-3"})
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
            obj['name'] = ahref.get("title").replace(".mp4","")

            videourl = urlparse(obj['url'])
            obj['path'] = "91gc"+videourl.path
            obj['rate'] = 1.2
            obj['updateTime'] = datetime.datetime.now() 
            obj['userId'] = userId
            obj['baseUrl'] = baseurl9
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
            url = url.replace("/index.php/vod/detail/id/","").replace(".html","")
            url = "%s%s%s"%("/index.php/vod/play/id/",url,"/sid/1/nid/1.html")
            soup = self.fetchUrl(baseurl9+url, header)
            div   = soup.first("div",{"class":"bofang_box"})
            if div !=None:
                text = unquote(str(div.text))
                texts = text.split(",")
                for item in texts:
                    match = regVideoM3.search(item)
                    if match!=None:
                        videoUrl =match.group(1).replace("\/","/")
                        return "%s%s%s"%("http",videoUrl,'m3u8')
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

