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
                if i!=1:
                    url = "%s%s%s"%(item['url'].replace(".html","-"),i,".html")
                print url
                self.videoParse(item['channel'], url,item['userId'])
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        ahrefs = self.headers("header12.html")
        channelList = []
        for ahref in ahrefs:
            obj={}
            obj['name']=ahref.text
            obj['url']=ahref.get('href')
            obj['baseUrl']=baseurl12
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1.2
            obj['channel']='天啦撸'
            obj['userId']="天啦撸"+ahref.text
            obj['showType']=3
            obj['channelType']='normal'
            channelList.append(obj)
        return channelList
    def videoParse(self, channel, url,userId):
        dataList = []
        soup = self.fetchUrl(baseurl12+url,header8)
        div = soup.first("div",{"class":"box dy_list"})
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
            obj['name'] = li.first("h3").text

            videourl = urlparse(obj['url'])
            obj['path'] = "tlula44"+videourl.path
            obj['rate'] = 1.2
            obj['updateTime'] = datetime.datetime.now() 
            obj['userId'] = userId
            obj['baseUrl'] = baseurl12
            obj['showType'] = 3
            obj['videoType'] = "webview"
            print obj['videoType'],obj['name'],mp4Url,obj['pic']
            dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideoUserItem(obj)

        print '天啦撸 video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
    def parseDomVideo(self, url):
        try:
            soup = self.fetchUrl(baseurl12+url, header)
            div   = soup.first("div",{"id":"dyplayer"})
            if div !=None:
                text = unquote(str(div.text))
                texts = text.split(",")
                for item in texts:
                    match = regVideoM3.search(item)
                    if match!=None:
                        videoUrl =match.group(1).replace("\/","/")
                        return "%s%s%s"%("https://ck.ckbfq.com/999player-tian.html?purl=http",videoUrl,'m3u8http://sd.52avhd.com:9888/zp/DEE4708C/SD/playlist.m3u8&h=610&url=www.tlula44.com&hd=0')
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

