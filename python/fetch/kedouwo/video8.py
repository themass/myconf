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
        print 'aotu user video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url= item['url']
                if i!=1:
                    url = "%s%s%s"%(item['url'],'/page/',i)
                print url
                self.videoParse(item['channel'], url,item['userId'])
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        ahrefs = self.header8()
        channelList = []
        for ahref in ahrefs:
            obj={}
            obj['name']=ahref.text
            obj['url']=ahref.get('href')
            obj['baseurl']=baseurl8
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1.2
            obj['channel']='经典蝌蚪窝'
            obj['userId']="v88hd"+ahref.text
            obj['showType']=3
            obj['channelType']='normal'
            channelList.append(obj)
        return channelList
    def videoParse(self, channel, url,userId):
        dataList = []
        soup = self.fetchUrl(baseurl8+url,header8)
        div = soup.first("div",{"class":"row listView"})
        if div!=None:
            lis = div.findAll("div",{"class":"col-xs-6 col-sm-6 col-md-4 contentItem"})
            for li in lis:
                ahref = li.first("a")
                obj = {}
                mp4Url = self.parseDomVideo(ahref.get("href"))
                if mp4Url == None:
                    print '没有mp4 文件:', ahref.get("href")
                    continue
                obj['url'] = mp4Url
                img = li.first("img")
                obj['pic'] = img.get("src")
                obj['name'] = li.first("a",{"class":"postTitle"}).text
    
                videourl = urlparse(obj['url'])
                obj['path'] = "8xqc"+videourl.path
                obj['rate'] = 1.2
                obj['updateTime'] = datetime.datetime.now() 
                obj['userId'] = userId
                obj['baseUrl'] = baseurl8
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

        print 'v88hd video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
        time.sleep(10)
    def parseDomVideo(self, url):
        try:
            soup = self.fetchUrl(baseurl8+url, header)
            div   = soup.first("span",{"id":"vpath"})
            if div !=None:
                return "%s%s"%("https://v.8xzizizi1.com/v/",div.text)
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

