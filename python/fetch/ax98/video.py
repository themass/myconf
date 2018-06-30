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
        ops.inertVideoChannel(chs)
        print ' channel ok; len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in urlList:
            for i in range(1, maxVideoPage):
                url= "%s%s%s"%(item,'?page=',i)
                self.videoParse(chs['channel'], url)
                print '解析完成 ', chs['channel'], ' ---', i, '页'
    def videoChannel(self):
        obj={}
        obj['name']='1分钟极速欣赏'
        obj['url']='one_minute'
        obj['baseurl']=baseurl
        obj['updateTime']=datetime.datetime.now()
        obj['pic']=''
        obj['rate']=1.2 
        obj['channel']=obj['url']
        obj['showType']=3
        obj['channelType']='list'
        return obj
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        lis = soup.findAll("li", {"itemprop": "itemListElement"})
        for li in lis:
            ahref = li.first('a')
            if ahref!=None:
                mp4Url  = self.parseDomVideo(ahref.get("href"))
                if mp4Url==None:
                    continue
                obj = {}
                obj['url'] = mp4Url
                img = li.first("img")
                pic = img.get('data-src')
                if pic==None:
                    pic=img.get('src')
                obj['pic'] = pic
                obj['name'] = img.get('alt')
                print obj['name'],mp4Url,obj['pic']

                videourl = urlparse(obj['url'])
                obj['path'] = videourl.path
                obj['updateTime'] = datetime.datetime.now()
                obj['channel'] = channel
                obj['baseurl'] = baseurl
                dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,"normal",baseurl)

        print 'ax98 video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
        try:
            soup = self.fetchUrl(url, header)
            source = soup.first('source')
            if source!=None:
                match = videoApi.search(source.get('src'))
                if match!=None:
                    return "%s%s%s"%("http",match.group(1),".m3u8")
            print url,'没有mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
