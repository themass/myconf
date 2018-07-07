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
        print 'sifangpian video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url = item['url']
                if i!=1:
                    url= "%s%s%s"%(item['url'].replace("1.html"),i,".html")
                print url
                self.videoParse(item['channel'], url)
                print '解析完成 ', item['baseurl'],item['channel'], ' ---', i, '页'
                time.sleep(1)
    def videoChannel(self):
        channelList = []
        obj={}
        obj['name']='生活日记'
        obj['url']='/vodtype/23/1.html'
        obj['baseurl']=baseurl
        obj['updateTime']=datetime.datetime.now()
        obj['pic']=''
        obj['rate']=1.2
        obj['channel']='sifangpian'
        obj['showType']=3
        obj['channelType']='normal'
        channelList.append(obj)
        return channelList
    def videoParse(self, channel, url):
        dataList = []
        print 'start'
        soup = self.fetchUrl(url)
        print 'end'
        metas = soup.findAll("div",{"class":"xb3 xl6 xm4 xs6 ul"})
        for meta in metas:
            obj = {}
            ahref = meta.first("a")
            mp4Url = self.parseDomVideo(ahref.get("href"))
            if mp4Url == None:
                print '没有mp4 文件:', ahref.get("href")
                continue
            obj['url'] = mp4Url
            obj['pic'] = baseurl+meta.first('img').get("data-original")
            obj['name'] = meta.first('img').get("alt")

            videourl = urlparse(mp4Url)
            obj['path'] = 'sifangpian_'+videourl.path
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

        print 'sifangpian video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
        try:
            soup = self.fetchUrl(url, header)
            scripts = soup.findAll("script")
            for script in scripts:
                text = unquote(script.text.replace("\"","").replace("\/","/"))
                texts = text.split(",")
                for item in texts:
                    match = regVideo.search(item)
                    if match!=None:
                        videoUrl =match.group(1)
                        return "%s%s%s"%("http://65c99cc8ecb8.cy1234.info:8888",videoUrl,'m3u8')
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None
