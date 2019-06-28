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
        print 'bxchua video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url = item['url']
                url= "%s%s%s%s"%(item['url'],"page_",i,".html")
                print url
                self.videoParse(item['channel'], url,item['baseurl'])
                print '解析完成 ', item['baseurl'],item['channel'], ' ---', i, '页'
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
            obj['rate']=1
            obj['channel']='bxchua'+ahref.text
            obj['showType']=3
            obj['channelType']='bxchua_all'
            channelList.append(obj)
#         channelList.reverse()
        return channelList
    def videoParse(self, channel, url,base):
        dataList = []
        soup = self.fetchUrl(url)
        metas = soup.findAll("div",{"class":"t_p"})
        for meta in metas:
            obj = {}
            ahref = meta.first("a")
            mp4Url = self.parseDomVideo(base,ahref.get("href"))
            if mp4Url == None:
                print '没有mp4 文件:', ahref.get("href")
                continue
            obj['url'] = mp4Url
            obj['pic'] = meta.first('img').get("data-original")
            obj['name'] = meta.first('h3').text
            if obj['name']==None or obj['name']=='None':
                h2 = ahref.first("h2")
                if h2!=None:
                    obj['name']=h2.text

            videourl = urlparse(mp4Url)
            obj['path'] = 'bxchua_'+videourl.path
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

        print '36kpd  video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
        time.sleep(0.5)
    def parseDomVideo(self, base,url):
        try:
            soup = self.fetchUrl(url, header)
            iframe = soup.first("span",{'id':'vpath'})
            if iframe!=None and iframe.text.count('index.m3u8')>0:
                return "%s%s"%(" https://jiuktp.com/v/",iframe.text)
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
