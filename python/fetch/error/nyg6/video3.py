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
                if ch['url'].count(".html")==1:
                    url= "%s%s%s"%(ch['url'],"?page=",i)
                else:
                    url= "%spage_%s.html"%(ch['url'],i)
                con = self.videoParse(ch['channel'],ch['channelType'], url)
                print '解析完成 ', ch['channel'], ' ---', i, '页'
                if con==False:
                    print '没有数据了啊-======页数',i,'---',ch['name'],ch['url']
                    break
    def videoChannel(self):
        objs = []
        
        ahrefs = self.header("header7.html")
        for html in ahrefs:
            obj = {}
            obj['name']=html.text
            obj['url']=html.get('href')
            obj['baseurl']=baseurl
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1.2
            obj['channel']='nyg6'+obj['name']
            obj['showType']=3
            obj['channelType']='nyg6_all_list'
            objs.append(obj)
        return  objs
    def videoParse(self, channel, channelType, url):
        dataList = []
        soup = self.fetchUrl(url)
        grids = soup.findAll("div",{"class":"grid_item "})
        if len(grids)==0:
            grids = soup.findAll("div",{"class":"grid_item"})
        if len(grids)==0:
            grids = soup.findAll("div",{"class":"grid_item grid_type1"})
        if len(grids)==0:
                return False
        for li in grids:
            ahref = li.first('a')
            if ahref!=None:
                mp4Url  = self.parseDomVideo(ahref.get("href"))
                if mp4Url==None:
                    continue
                obj = {}
                obj['url'] = mp4Url
                img = li.first("img")
                obj['pic'] = img.get("data-src").replace("?max-age=3600","")
                obj['name'] = li.first("p").text
                print obj['name'],mp4Url,obj['pic']

                videourl = urlparse(obj['url'])
                obj['path'] = "nyg6"+channel+videourl.path
                obj['updateTime'] = datetime.datetime.now()
                obj['channel'] = channel
                obj['baseurl'] = baseurl
                dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,"normal",baseurl,channelType)

        print 'nyg6 video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
        if len(dataList)==0:
            return False
        return True

    def parseDomVideo(self, url):
        try:
            soup = self.fetchUrl(url)
            videoUrl = soup.first("input",{"id":"videoUrl"})
            if videoUrl!=None:
                return videoUrl.get("value")
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None
