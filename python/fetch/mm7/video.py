#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from urllib import unquote
import time
from fetch.profile import *
class VideoUserParse(BaseParse):

    def __init__(self,name):
        self.t_name = name

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        chs = self.videoChannel()
        for item in chs:
            ops.inertVideoUser(item)
        print 'mm7 user video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            soup = self.fetchUrl(item['url'])
            span = soup.first("span", {"class":"page_previous"})
            maxPage = maxVideoPage
            if span!=None and span.first("a")!=None:
                try:
                    maxPage = int(span.first("a").text)
                except Exception as e:
                    pass
            print "max page=",maxPage,item['url']
            for i in range(1, maxPage):
                url = item['url']
                url= "%s%s%s"%(item['url'].replace("random/all/index.html","list/all/"),i,".html")
                print url
                self.videoParse(item['channel'], url,item['userId'])
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        ahrefs = self.header(self.t_name)
        channelList = []
        for ahref in ahrefs:
            obj={}
            obj['name']=ahref.text
            obj['url']=ahref.get('href')
            obj['baseUrl']=baseurl
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1.2
            obj['channel']='mm7_all'
            obj['userId']="mm7_"+ahref.text
            obj['showType']=3
            channelList.append(obj)
        return channelList
    def videoParse(self, channel, url,userId):
        dataList = []
        soup = self.fetchUrl(url)
        metas = soup.findAll("div", {"class": "col-xs-50  col-sm-33 col-lg-25"})
        print url,len(metas)
        for meta in metas:
            obj = {}
            ahref = meta.first("a")
            mp4Url = self.parseDomVideo(ahref.get("href"))
            if mp4Url == None:
                print '没有mp4 文件:', ahref.get("href")
                continue
            img = ""
            title = ""
            if meta.first('video')==None:
                img = meta.first('img').get("src")
            else:
                img = meta.first('video').get("poster")
            title= meta.first('h2').text 
            obj['url'] = mp4Url
            obj['pic'] = img
            obj['name'] = title

            videourl = urlparse(obj['url'])
            obj['path'] = 'mm7_'+videourl.path
            obj['updateTime'] = datetime.datetime.now()
            obj['channel'] = channel
            if mp4Url.count("m3u8")==0 and mp4Url.count("mp4")==0:
                obj['videoType'] = "webview"
            else:
                obj['videoType'] = "normal"
            obj['baseUrl'] = baseurl
            obj['rate'] = 1.2
            obj['userId'] = userId
            obj['showType'] = 3
            print obj['name'],obj['videoType'],obj['url'],obj['pic']
            
            dataList.append(obj)
                
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideoUserItem(obj)

        print 'mm7 video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
        try:
            soup = self.fetchUrl(url, header)
            scripts = soup.findAll("script")
            for script in scripts:
                text = unquote(script.text)
                texts = text.split("iframe")
                for item in texts:
#                     print item
                    match = regVideo2.search(item)
                    if match!=None:
                        soup=self.fetchUrlWithBase("%s%s%s"%(match.group(1),"/",match.group(2)),header)
                        source = soup.first("source")
                        if source!=None:
                            return source.get("src")
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

