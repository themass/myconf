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
        print 'nyg6 user video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url= "%s%s%s"%(item['url'],"?page=",i)
                print url
                self.videoParse(item['channel'], url,item['userId'])
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        channelList = []
        
        ahrefs = self.header("header.html")
        for ahref in ahrefs:
            for i in range(1, 10):
                url= "%spage_%s.html"%(ahref.get("href"),i)
                soup = self.fetchUrl(url)
                grids = soup.findAll("div",{"class":"grid_item"})
                for item in grids:
                    obj={}
                    obj['name']=item.first("p").text
                    obj['url']=item.first("a").get('href')
                    obj['baseUrl']=baseurl
                    obj['updateTime']=datetime.datetime.now()
                    obj['pic']=''
                    obj['rate']=1.2
                    obj['channel']=ahref.text
                    obj['userId']="nyg6"+obj['name']
                    obj['showType']=3
                    obj['channelType']='normal'
                    channelList.append(obj)
        return channelList
    def videoParse(self, channel, url,userId):
        dataList = []
        soup = self.fetchUrl(url)
        lis = soup.findAll("div",{"class":"grid_item"})
        for li in lis:
            #name,pic,url,userId,rate,updateTime,path
            ahref = li.first("a")
            if ahref!=None:
                obj = {}
                mp4Url = self.parseDomVideo(ahref.get("href"))
                if mp4Url == None:
                    print '没有mp4 文件:', ahref.get("href")
                    continue
                obj['url'] = mp4Url
                img = li.first("img")
                if img.get("src").count("http")==0:
                    obj['pic'] = baseurl+img.get("data-src")
                else:
                    obj['pic'] = img.get("data-src").replace("?max-age=3600","")
                obj['name'] = li.first("p").text
    
                videourl = urlparse(obj['url'])
                obj['path'] = userId+videourl.path
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

        print 'nyg6 video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
        header = {'User-Agent':
                  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": url}
        try:
            soup = self.fetchUrl(url, header)
            videoUrl = soup.first("input",{"id":"videoUrl"})
            if videoUrl!=None:
                return videoUrl.get("value")
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

