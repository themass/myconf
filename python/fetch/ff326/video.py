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
        print '326ff user video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url= "%s%s%s"%(item['url'],i,".htm")
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
            obj['channel']='藏经阁'
            obj['userId']='326ff_'+ahref.text
            obj['showType']=3
            obj['channelType']='normal'
            channelList.append(obj)
        return channelList
    def videoParse(self, channel, url,userId):
        dataList = []
        soup = self.fetchUrl(url)
        lis = soup.findAll("li",{"class":"col-md-2 col-sm-3 col-xs-4"})
        for li in lis:
            ahref = li.first("a")
            #name,pic,url,userId,rate,updateTime,path
            obj = {}
            mp4Url = self.parseDomVideo(ahref.get("href"))
            if mp4Url == None:
                print '没有mp4 文件:', ahref.get("href")
                continue
            obj['url'] = mp4Url
#                 img = ahref.first("img")
#                 if img.get("src").count("http")==0:
#                     obj['pic'] = img.get("src")
#                 else:
#                     obj['pic'] = img.get("src")
            obj['pic'] = ahref.get("data-original")
            
            obj['name'] = ahref.get('title').replace("'","")

            videourl = urlparse(obj['url'])
            obj['path'] = "326ff"+videourl.path
            obj['rate'] = 1.2
            obj['updateTime'] = datetime.datetime.now()
            obj['userId'] = userId
            obj['baseUrl'] = baseurl
            obj['showType'] = 3
            if mp4Url.count(".m3u8")==0 and mp4Url.count(".mp4")==0:
                obj['videoType'] = "webview"
            else:
                obj['videoType'] = "normal"
            print obj['videoType'],mp4Url,obj['name'],obj['pic']
            dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideoUserItem(obj)

        print '326ff video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
        try:
            soup = self.fetchUrl(url)
            div = soup.first("div",{"id":"mp4play"})
            if div!=None:
                href = div.first("a")
                if href!=None:
                    soup = self.fetchUrl(href.get("href"))
                    scripts = soup.findAll("script")
                    for script in scripts:
                        text = unquote(str(script.text)).replace(' ', '')
                        
                        match = iframeVideo2.search(text)
                        if match!=None:
                            iframeurl = match.group(1).replace("'","").replace("+","").replace(" ","")
                            return "%s%s"%("https://xin.170du.com/",iframeurl)
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

