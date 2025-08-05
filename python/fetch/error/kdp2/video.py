#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from urllib import unquote
import time
from fetch.profile import *
from baseparse import baseurl

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
                    url= "%s%s%s"%(ch['url'].replace('.html','_'),i,'.html')
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
        div = soup.first("div", {"class": "list mb"})
        if div!=None:
            lis = div.findAll("li")
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
                    img = ahref.first("img")
                    obj['pic'] = img.get('src')
                    obj['name'] = ahref.get("title")
                    obj['path'] = "2828_%s%s%s"%(channel,"-",obj['name'])
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

    def parseDomVideo(self, url):
        try:
            url = url.replace("/bbb/","").replace(".html","")
            url = "/ccc/%s-0-0.html"%(url)
            soup = self.fetchUrl(url)
            ul = soup.first('div',{"class":'player'})
            if ul!=None and ul.first("script")!=None:
                co = self.fetchContentUrlWithBase(baseurl+ul.first("script").get("src"))
                texts = unquote(co).replace(")","$").replace("http://player.ly6080.com/yunparse/?url=", "").replace("http://player.ly6080.com/odflv/index.php?url=", "").split("$")
                texts.reverse()
                for text in texts:
                    match = videoApi.search(text)
                    if match!=None:
                        str= match.group(1)
                        return "%s%s%s"%("http",str,".m3u8")
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
