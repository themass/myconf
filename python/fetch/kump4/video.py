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
                url =ch['url']
                if i!=1:
                    url= "%s%s%s"%(url.replace('.html','_'),i,'.html')
                self.videoParse(ch['channel'], url)
                print '解析完成 ', ch['channel'], ' ---', i, '页'
    def videoChannel(self):
        soup = self.fetchUrl('/')
        div = soup.first("div", {"class": "nav_1000"})
        if div!=None:
            objs =[]
            asList = div.findAll('a')
            for ahref in asList:
                obj={}
                obj['name']=ahref.text
                obj['url']=ahref.get('href')
                obj['baseurl']=baseurl
                obj['updateTime']=datetime.datetime.now()
                obj['pic']=''
                obj['rate']=1.2
                obj['channel']=obj['name']
                obj['showType']=3
                obj['channelType']='movie'
                objs.append(obj)
        return objs
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        lis = soup.findAll("div", {"class": "li_all"})
        for li in lis:
            ahref = li.first('a')
            if ahref!=None:
                mp4Url  = self.parseDomVideo(ahref.get("href"))
                if mp4Url==None:
                    continue
                obj = {}
                obj['url'] = mp4Url
                img = li.first("img")
                pic = img.get('src')
                obj['pic'] = pic
                name = li.first('div',{"class":"li_text"}).first('a').text
                obj['name'] = name
                if name.count('TS')!=0:
                    print 'TS版本，略过---',name
                    continue
                obj['path'] = "%s%s%s"%(channel,"-",obj['name'])
                print obj['path'],obj['url'],obj['pic']
                obj['updateTime'] = datetime.datetime.now()
                obj['channel'] = channel
                obj['baseurl'] = baseurl
                dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,"normal",baseurl)

        print 'kump4 video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
        try:
            soup = self.fetchUrl(url, header)
            div = soup.first('div',{"class":"stab_list"})
            if div!=None:
                ahref = div.first('a')
                if ahref!=None:
                    soup = self.fetchUrl(ahref.get('href'), header)
                    player = soup.first('div',{"class":"player"})
                    if player!=None:
                        content = unquote(str(player.text)).split("$")
                        for item in content:
                            match = regVideo.search(item)
                            if match!=None: 
                                return "http"+match.group(1)+'.m3u8'
                    
            print url,'没有mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
