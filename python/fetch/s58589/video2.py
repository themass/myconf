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
        print '6hu58 user video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url = item['url']
                if i!=1:
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
            obj['baseurl']=baseurl
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1.2
            obj['channel']='s58589_all'
            obj['userId']="s58589_"+ahref.text
            obj['showType']=3
            channelList.append(obj)
        return channelList
    def videoParse(self, channel, url,userId):
        dataList = []
        soup = self.fetchUrl(url)
        metas = soup.findAll("li", {"class": "yun yun-large border-gray"})
        for meta in metas:
            obj = {}
            ahref = meta.first("a")
            mp4Url = self.parseDomVideo(ahref.get("href"))
            if mp4Url == None:
                print '没有mp4 文件:', ahref.get("href")
                continue
            obj['url'] = mp4Url
            obj['pic'] = meta.first('img').get("data-original")
            obj['name'] = ahref.get("title").replace("，快播，大香蕉","").replace("_chunk_1,快播云资源","").replace("成人影院","")

            videourl = urlparse(obj['url'])
            obj['path'] = '58589_'+videourl.path
            obj['updateTime'] = datetime.datetime.now()
            obj['channel'] = channel
            if mp4Url.count("m3u8")==0 and mp4Url.count("mp4")==0:
                obj['videoType'] = "webview"
            else:
                obj['videoType'] = "normal"
            obj['baseurl'] = baseurl
            obj['rate'] = 1.2
            obj['userId'] = userId
            obj['showType'] = 3
            print obj['name'],obj['videoType'],obj['url'],obj['pic']
            
            dataList.append(obj)
                
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideoUserItem(obj)

        print '58589 video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
        try:
            soup = self.fetchUrl(url, header)
            div = soup.first("div",{'class':'playlist jsplist clearfix'})
            if div!=None:
                ahref = div.first('a')
                if ahref!=None:
                    soup = self.fetchUrl(ahref.get('href'), header)
                    play_video = soup.first('div',{'class':'video-info fn-left'})
                    if play_video!=None:
                        script = play_video.first('script')
                        if script!=None:
                            text = unquote(script.text.replace("\"","").replace("\/","/"))
                            texts = text.split(",")
                            for item in texts:
                                match = regVideo.search(item)
                                if match!=None:
                                    videoUrl =match.group(1)
                                    return "%s%s%s"%("http",videoUrl,'m3u8')
                                match = regVideo2.search(item)
                                if match!=None:
                                    videoUrl =match.group(1)
                                    return videoUrl
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

