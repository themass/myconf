#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from urllib import unquote
import time
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
        print 'zanquye video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url= item['url']
                if i!=1:
                    url= "%s%s%s"%(item['url'].replace('.html','-'),i,".html")
                self.videoParse(item['channel'], url)
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        soup = self.fetchUrl('/')
        div  = soup.first('ul',{'class':'dropdown-menu'})
        channelList =[]
        if div!=None:
            ahrefs = div.findAll('a')
            for ahref in ahrefs:
                if ahref.text=="伦理片" or ahref.text=="激情福利":
                    obj={}
                    obj['name']=ahref.text
                    obj['url']=ahref.get('href')
                    obj['baseurl']=baseurl
                    obj['updateTime']=datetime.datetime.now()
                    obj['pic']=''
                    obj['rate']=0.7
                    obj['channel']=obj['name']=ahref.text
                    obj['showType']=1
                    obj['channelType']='movie'
                    channelList.append(obj)
        return channelList
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        lis = soup.findAll("li",{"class":'col-md-2 col-sm-2 col-xs-4 text-center sea-vod-img-new sea-col'})
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
                obj['pic'] = baseurl+img.get("src")
                obj['name'] = img.get("alt")
                obj['path'] = "%s%s%s"%(channel,"-",obj['name'])
                obj['updateTime'] = datetime.datetime.now()
                if mp4Url.count("m3u8")==0:
                    obj['videoType'] = "movie"
                else:
                    obj['videoType'] = "normal"
                obj['channel'] = channel
                obj['baseurl'] = baseurl
                print obj['videoType'],obj['url'],obj['pic']
                dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,obj['videoType'],baseurl)

        print 'zanquye video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
      
        try:
            soup = self.fetchUrl(url)
            tabContent = soup.first("div",{"class":"tab-content"})
            div = tabContent.first("div")
            if div!=None:
                ahref = div.first("a")
                if ahref!=None:
                    soup = self.fetchUrl(ahref.get("href"))
                    player = soup.first("div",{"class":"player"})
                    if player!=None:
                        script = player.first("script")
                        if script!=None:
                            content = unquote(str(script.text)).split("$")
                            for item in content:
                                match = regVideo.search(item)
                                if match!=None: 
                                    return "http"+match.group(1)+'m3u8'
                                elif content.count(regVideoYun)>0:
                                    return content
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
