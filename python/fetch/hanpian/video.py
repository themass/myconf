#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from urllib import unquote
import time,json
from fetch.profile import *
from urllib import unquote

class VideoParse(BaseParse):

    def __init__(self):
        pass

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        chs = self.videoChannel()
        for item in chs:
            ops.inertVideoChannel(item)
        print 'hanpian video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url= item['url']
                if i!=1:
                    url= "%s%s%s"%(item['url'].replace('.html','-pg-'),i,".html")
                self.videoParse(item['channel'], url)
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        channelList = []
#         for ahref in ahrefs:
#             if ahref.text!="全部":
#                 obj={}
#                 obj['url']=ahref.get('href')
#                 obj['baseurl']=baseurl
#                 obj['updateTime']=datetime.datetime.now()
#                 obj['pic']=''
#                 obj['rate']=0.7
#                 obj['channel']=obj['name']=ahref.text+"片"
#                 obj['showType']=1
#                 obj['channelType']='movie'
#                 obj['page']=20
#                 channelList.append(obj)
                
        obj={}
        obj['url']='/index.php?m=vod-type-id-16.html'
        obj['baseurl']=baseurl
        obj['updateTime']=datetime.datetime.now()
        obj['pic']=''
        obj['rate']=1.2
        obj['channel']=obj['name']='伦理片4'
        obj['showType']=3
        obj['channelType']='movie'
        channelList.append(obj)
        return channelList
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        lis = soup.findAll("div",{"class":'li_li clearfix'})
        for li in lis:
            ahref = li.first('a')
            if ahref != None:
                obj = {}
                mp4Url = self.parseDomVideo(ahref.get("href"))
                if mp4Url == None:
                    print '没有mp4 文件:', ahref.get("href")
                    continue
                obj['url'] = mp4Url
                img = ahref.first("img")
                obj['pic'] =img.get("src")
                obj['name'] = li.first('a',{"class":"alink"}).get("title")
                obj['path'] = "%s%s%s"%(channel,"-",obj['name'])
                obj['updateTime'] = datetime.datetime.now()
                if mp4Url.count("m3u8")==0 and mp4Url.count("mp4")==0:
                    obj['videoType'] = "webview"
                else:
                    obj['videoType'] = "normal"
                obj['channel'] = channel
                obj['baseurl'] = baseurl
                print obj['name'],obj['url'],obj['pic']
                dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,obj['videoType'],baseurl)

        print 'hanpian video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
      
        try:
            soup = self.fetchUrl(url)
            div = soup.first("div",{"class":"playlist clearfix"})
            if div!=None:
                aherf = div.first("a")
                if aherf !=None:
                    soup = self.fetchUrl(aherf.get('href'))
                    playerall = soup.first("div",{"class":"playerall"})
                    script  = playerall.first("script")
                    if script !=None:
                        content = unquote(str(script.text)).replace("#","$").replace("');","$").split("$")
                        for item in content:
                            match = regVideo.search(item)
                            if match!=None: 
                                return "http"+match.group(1)+'m3u8'
                        for item in content:
                            if item.count(regVideoyun)>0:
                                return item
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
