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
        print 'cd1988 video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url= item['url']
                if i!=1:
                    url= "%s%s%s"%(item['url'].replace('1.html',''),i,".html")
                self.videoParse(item['channel'], url)
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        soup = self.fetchUrl("/")
        div = soup.first("div",{"class":"nav-down-2 clearfix"})
        ahrefs = div.findAll("a")
        channelList = []
        for ahref in ahrefs:
            if ahref.text!="全部":
                obj={}
                obj['url']=ahref.get('href')
                obj['baseurl']=baseurl
                obj['updateTime']=datetime.datetime.now()
                obj['pic']=''
                obj['rate']=1.2
                obj['channel']=obj['name']=ahref.text
                obj['showType']=3
                obj['channelType']='movie'
                channelList.append(obj)
        channelList.append(obj)
        return channelList
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        lis = soup.findAll("li",{"class":'p1 m1'})
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
                obj['pic'] =img.get("data-original")
                obj['name'] = img.get("alt")
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

        print 'cd1988 video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
      
        try:
            match = regVideoNum.search(url)
            if match!=None:
                num = match.group(1)
                itemurl = "%%%"%("/playtv/",num,".html")
                soup = self.fetchUrl(itemurl)
            div = soup.first("div",{"class":"playlist"})
            if div!=None:
                aherf = div.first("a")
                if aherf !=None:
                    soup = self.fetchUrl(aherf.get('href'))
                    playerall = soup.first("div",{"class":"playerall"})
                    script  = playerall.first("script")
                    if script !=None:
                        url = script.get("src")
                        content = unquote(str(script.text))
                        if url!=None:
                            content = self.fetchContentUrlWithBase(script.get("src"))
                            content = unquote(str(content))
                        match = regVideo.search(content)
                        if match!=None:
                            obj = json.loads(match.group(1))
                            return obj.get('url',None)
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
