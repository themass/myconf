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
        print 'youjiady video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url= "/%s%s%s%s"%(item['url'],"&","page=",i)
                print url
                self.videoParse(item['channel'], url)
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        ahrefs = self.header()
        channelList = []
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
            obj['channelType']='normal'
            channelList.append(obj)
        return channelList
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        alist = soup.findAll("a", {"class": "videopic lazy"})
        for ahref in alist:
            obj = {}
            mp4Url = self.parseDomVideo(ahref.get("href"))
            if mp4Url == None:
                print '没有mp4 文件:', ahref.get("href")
                continue
            obj['url'] = mp4Url
            obj['pic'] = ahref.get("data-original").replace("#err","")
            obj['name'] = ahref.get('title')

            videourl = urlparse(obj['url'])
            obj['path'] = videourl.path
            obj['updateTime'] = datetime.datetime.now()
            obj['channel'] = channel
            if mp4Url.count("m3u8")==0 and mp4Url.count("mp4")==0:
                obj['videoType'] = "webview"
            else:
                obj['videoType'] = "normal"
            print obj['videoType'],obj['name'],mp4Url,obj['pic']
            dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,obj['videoType'] ,baseurl)

        print '44iir video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
        header = {'User-Agent':
                  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": url}
        try:
            url = url.replace("/detail/","").replace(".html","")
            url = "%s%s%s"%("/video/?",url,"-0-0.html")
            soup = self.fetchUrl(url, header)
            play_video = soup.first('div',{'class':'info clearfix'})
            if play_video!=None:
                script = play_video.first('script')
                if script!=None:
                    text = unquote(script.text)
                    texts = text.split("$")
                    for item in texts:
                        match = regVideo.search(item)
                        if match!=None:
                            videoUrl =match.group(1)
                            return "%s%s%s"%("http",videoUrl,'m3u8')
                    for item in texts:
                        match = shareVideo.search(text)
                        if match!=None:
                            videoUrl ="%s%s%s%s"%("http",match.group(1),"/share/",match.group(2))
                            return videoUrl
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
