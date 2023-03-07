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
        chs  = self.videoChannel()
        for ch in chs:
            ops.inertVideoChannel(ch)
        print ' channel ok; len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for ch in chs:
            for i in range(1, maxVideoPage):
                url= ch['url'].replace(".html",'')
                url= "%s--------%s---%s"%(url,i,'.html')
                self.videoParse(ch['channel'], ch['channelType'], url)
                print '解析完成 ', ch['channel'], ' ---', i, '页'
    def videoChannel(self):
        channelList = []
        ahrefs = self.header()
        for ahref in ahrefs:
            obj={}
            obj['name']=ahref.text
            obj['url']=ahref.get('href')
            obj['baseurl']=baseurl
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1.2
            obj['channel']=obj['name']
            obj['showType']=3
            obj['channelType']='movie'
            channelList.append(obj)
#         channelList.reverse()
        return  channelList
    def videoParse(self, channel, channelType, url):
        dataList = []
        soup = self.fetchUrl(url)
        ahrefs = soup.findAll("a", {"class": "macplus-vodlist__thumb lazyload"})
        for ahref in ahrefs:
            if ahref!=None:
                mp4Url  = self.parseDomVideo(ahref.get("href"))
                if mp4Url==None:
                    continue
                if mp4Url.count('.html')!=0 :
                    print mp4Url,"爱奇艺，忽略"
                    continue
                obj = {}
                obj['url'] = mp4Url
                obj['pic'] = ahref.get("data-original")
                obj['name'] = ahref.get("title")
                if obj['name']!=None and obj['name'].count("预告")!=0:
                    continue
                obj['path'] = "xcvods_%s%s%s"%(channel,"-",obj['name'])
                if mp4Url.count("m3u8")==0 and mp4Url.count("mp4")==0:
                    obj['videoType'] = "webview"
                else:
                    obj['videoType'] = "normal"
                print obj['videoType'],obj['name'],mp4Url,obj['pic']
                obj['updateTime'] = datetime.datetime.now()
                obj['channel'] = channel
                obj['baseurl'] = baseurl
                dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,obj['videoType'],baseurl,channelType)

        print 'xcvods video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
        time.sleep(5)

    def parseDomVideo(self, url):
        header = {"User-Agent":"Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)", "Referer": url}
        try:
            match = videoId.search(url)
            if match!=None:
                Id= match.group(2)
                url  = 'vod-play-id-%s-src-1-num-1.html'%(Id)
                soup = self.fetchUrl(url, header)
                div = soup.first('div',{'class':'macplus-player__video embed-responsive embed-responsive-16by9'})
                if div!= None:
                    scripts = div.findAll("script")
                    for script in scripts:
                        text = unquote(script.text.replace("\"","").replace("\/","/").replace(" ",''))
                        lines = text.split(",")
                        for t in lines:
                            match = videoApi.search(text)
                            if match!=None:
                                videoUrl =match.group(1)
                                return "%s%s%s"%("http",videoUrl,'.m3u8')
                print '没找到mp4',url
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
