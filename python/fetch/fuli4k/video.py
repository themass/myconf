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
                    url= "%s%s%s"%(ch['url'],"&page=",i)
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
            obj['channel']='4k_'+obj['name']
            obj['showType']=3
            obj['channelType']='4kfuli_all'
            channelList.append(obj)
#         channelList.reverse()
        return  channelList
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        lis = soup.findAll("div",{"class":"col-md-1-5 col-sm-4 col-xs-6"})
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
                obj['pic']=ahref.first("img").get("src")
                obj['name'] = ahref.get("title")
                obj['path'] = "%s%s%s"%(channel,"-",obj['name'])
                print obj['path'],obj['url'],obj['pic']
                obj['updateTime'] = datetime.datetime.now()
                obj['channel'] = channel
                obj['baseurl'] = baseurl
                dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,"webview",baseurl)

        print 'f8dy video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
        header = {'User-Agent':
                  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": url}
        try:
            soup = self.fetchUrl(url.replace("show","play"), header)
            iframe = soup.first('iframe')
            if iframe!=None:
                if iframe.get("src").startswith("http"):
                    return iframe.get("src")
                else:
                    return baseurl+iframe.get("src")
            print url,'没有mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
