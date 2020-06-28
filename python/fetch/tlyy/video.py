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
                url= ch['url']
                if i!=1:
                    url= "%s%s%s"%(url,i,'.html')
                self.videoParse(ch['channel'], url)
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
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        ul = soup.first("ul", {"class":"watch"})
        if ul!=None:
            lis = ul.findAll("li")
            for li in lis:
                ahref = li.first('a')
                if ahref!=None:
                    mp4Url  = self.parseDomVideo(ahref.get("href"))
                    if mp4Url==None:
                        continue
                    if mp4Url.count('.html')!=0 :
                        print mp4Url,"爱奇艺，忽略"
                        continue
                    obj = {}
                    obj['url'] = mp4Url
                    obj['pic'] = li.first('img').get("src")
                    obj['name'] = li.first('img').get("alt")
                    obj['path'] = "tlyy_%s%s%s"%(channel,"-",obj['name'])
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
            ops.inertVideo(obj,obj['videoType'],baseurl)

        print 'f8dy video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
        time.sleep(5)

    def parseDomVideo(self, url):
        header = {"User-Agent":"Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)", "Referer": url}
        try:
            soup = self.fetchUrl(url, header)
            div = soup.first('div',{"class":'bluebd'})
            if div!=None:
                url=div.first('a').get("href")
                soup = self.fetchUrl(url, header)
                div = soup.first('div',{"class":'play-container'})
                if div!=None:
                    script = div.first("script")
                    if script!=None:
                        texts = self.fetchContentUrlWithBase(baseurl+script.get("src"), aheader)
                        texts = unquote(texts).split("$")
                        for text in texts:
                            match = videoApi.search(text)
                            if match!=None:
                                str= match.group(1)
                                return "%s%s%s"%("http",str,".m3u8")
                        for text in texts:
                            match = videoApiMp4.search(text)
                            if match!=None:
                                str= match.group(1)
                                return "%s%s%s"%("http",str,".mp4")
                        for text in texts:
                            match = shareVideo.search(text)
                            if match!=None:
                                return text.replace("'",'').replace(")",'').replace(";",'')
            print url,'没有mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
