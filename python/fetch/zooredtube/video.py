#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from urllib import unquote
import time
from fetch.profile import *
class VideoParse(BaseParse):

    def __init__(self):
        pass

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        chs = self.videoChannel()
        for item in chs:
            ops.inertVideoChannel(item)
        ops.deleteVideoItems(baseurl)
        
        print 'zoo video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, 25):
                url = '/'
                if i!=1:
                    url= "%s%s%s"%('/',i,"/")
                print url
                self.videoParse(item['channel'], url)
                print '解析完成 ', item['channel'], ' ---', i, '页'
                time.sleep(1)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        ops.updateVideoItemsChannelType()
        dbVPN.commit()
        dbVPN.close()
    def videoChannel(self):
        channelList = []
        obj={}
        obj['name']='动物大世界'
        obj['url']='bestzoovi'
        obj['baseurl']=baseurl
        obj['updateTime']=datetime.datetime.now()
        obj['pic']=''
        obj['rate']=1.2
        obj['channel']='zooredtube'
        obj['showType']=3
        obj['channelType']='normal'
        channelList.append(obj)
        return channelList
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        metas = soup.findAll("li",{"class":"item thumb"})
        for meta in metas:
            obj = {}
            ahref = meta.first("a")
            mp4Url = self.parseDomVideo(ahref.get("href"))
            if mp4Url == None:
                print '没有mp4 文件:', ahref.get("href")
                continue
            obj['url'] = mp4Url
            img = meta.first('img')
            obj['pic'] = img.get("src")
            obj['name'] = img.get("alt")

            videourl = urlparse(obj['url'])
            obj['path'] = videourl.path
            obj['updateTime'] = datetime.datetime.now()
            obj['channel'] = channel
            if mp4Url.count("m3u8")==0 and mp4Url.count("mp4")==0:
                obj['videoType'] = "webview"
            else:
                obj['videoType'] = "normal"
            obj['baseurl'] = baseurl
            print obj['name'],obj['videoType'],obj['url'],obj['pic']
            dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,obj['videoType'],baseurl)

        print 'lushibi video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
        try:
            soup = self.fetchUrl(url, header)
            scripts = soup.findAll("script")
            for script in scripts:
                text = unquote(script.text.replace("\"","").replace("\/","/"))
                match = regVideo.search(text)
                if match!=None:
                    videoUrl =match.group(1)
                    return "%s%s"%("http",videoUrl)
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
