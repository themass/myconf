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
        print 'avhome user video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url = item['url']
                if i!=1:
                    url= "/%s%s%s%s"%(item['url'],"index-",i,".html")
                print url
                self.videoParse(item['channel'], url,item['userId'])
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        ahrefs = self.header("header.html")
        channelList = []
        for ahref in ahrefs:
            obj={}
            obj['name']=ahref.text
            obj['url']=ahref.get('href')
            obj['baseurl']=baseurl
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1.2
            obj['channel']='avhome-all'
            obj['userId']=ahref.text
            obj['showType']=3
            obj['channelType']='normal'
            channelList.append(obj)
        return channelList
    def videoParse(self, channel, url,userId):
        dataList = []
        soup = self.fetchUrl(url)
        div = soup.first("div", {"id": "box movie_list"})
        if div!=None:
            lis = div.findAll("li")
            for li in lis:
                #name,pic,url,userId,rate,updateTime,path
                ahref = li.first("a")
                obj = {}
                mp4Url = self.parseDomVideo(ahref.get("href"))
                if mp4Url == None:
                    print '没有mp4 文件:', ahref.get("href")
                    continue
                obj['url'] = mp4Url
                img = ahref.first("img")
                if img.get("src").count("http")==0:
                    obj['pic'] = baseurl+img.get("src")
                else:
                    obj['pic'] = img.get("src")
                obj['name'] = img.get('alt')
    
                videourl = urlparse(obj['url'])
                obj['path'] = "avhome"+videourl.path
                obj['rate'] = 1.2
                obj['updateTime'] = datetime.datetime.now()
                obj['userId'] = userId
                obj['baseUrl'] = baseurl
                obj['showType'] = 3
                if mp4Url.count("m3u8")==0 and mp4Url.count("mp4")==0:
                    obj['videoType'] = "webview"
                else:
                    obj['videoType'] = "normal"
                print obj['videoType'],obj['name'],mp4Url,obj['pic']
                dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideoUserItem(obj)

        print 'avhome video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
        try:
            soup = self.fetchUrl(url)
            adiv = soup.first("div",{"class":"film_bar clearfix"})
            if adiv!=None:
                ahref = adiv.first("a")
                if ahref!=None:
                    soup = self.fetchUrl(ahref.get("href"), header)
                    scripts = soup.findAll("script")
                    for script in scripts:
                        jsHref = script.get("src")
                        if jsHref!=None and jsHref.count("upload")>0:
                            text = self.fetchContentUrlWithBase(baseurl+jsHref)
                            text = unquote(str(text))
                            texts = text.split("$")
                            for item in texts:
                                match = videoApi.search(item)
                                if match!=None:
                                    videoUrl =match.group(1)
                                    return "%s%s%s"%("http",videoUrl,'m3u8')
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

