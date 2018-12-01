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
        print 'xshare video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url = item['url']
                if i!=1:
                    url= "%s%s%s"%(item['url'].replace(".html","-"),i,".html")
                print url
                count = self.videoParse(item['channel'], url)
                print '解析完成 ', item['baseurl'],item['channel'], ' ---', i, '页'
                if count ==0:
                    break
    def videoChannel(self):
        channelList = []
        ahrefs = self.header("header.html")
        for ahref in ahrefs:
            obj={}
            obj['name']=ahref.text
            obj['url']=ahref.get('href')
            obj['baseurl']=baseurl
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1.2
            obj['channel']=ahref.text
            obj['showType']=3
            obj['channelType']='movie'
            channelList.append(obj)
        return channelList
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        metas = soup.findAll("div",{"class":"col-xs-12 col-sm-6 col-md-6 col-lg-4"})
        if len(metas)==0:
            return 0
        for meta in metas:
            obj = {}
            ahref = meta.first("a")
            mp4Url = self.parseDomVideo(ahref.get("href"))
            if mp4Url == None:
                print '没有mp4 文件:', ahref.get("href")
                continue
            obj['url'] = mp4Url
            obj['pic'] = meta.first('img').get("src")
            obj['name'] = ahref.get("title")

            videourl = urlparse(mp4Url)
            obj['path'] = videourl.path
            obj['updateTime'] = datetime.datetime.now()
            obj['channel'] = channel
            obj['videoType'] = "normal"
            obj['baseurl'] = baseurl
            print obj['name'],obj['videoType'],obj['url'],obj['pic']
            dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,obj['videoType'],baseurl)

        print 'xshare video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
        return len(dataList)
    def parseDomVideo(self, url):
        try:
            soup = self.fetchUrl(url)
            divs = soup.findAll("ul",{'class':'play-list play-list-long'})
            for div  in divs:
                ahref = div.first("a")
                soup = self.fetchContentUrl(ahref.get("href"))
#                 scripts = soup.findAll('script')
#                 scripts.reverse()
#                 for script in scripts: 
#                     text = unquote(script.text.replace("\"","").replace("\/","/"))
#                     print text
                match = regVideo.search(soup)
                if match!=None:
                    videoUrl =match.group(1)
                    return "%s%s%s"%("http",videoUrl,'m3u8')
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
