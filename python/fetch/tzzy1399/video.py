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
        chs = self.videoChannel()
        for item in chs:
            ops.inertVideoChannel(item)
        print '99tzzy13 video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url= item['url']
                url = "%s%s%s"%(url.replace('.html','-p-'),i,'.html')
                self.videoParse(item['channel'], url)
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        soup = self.fetchUrl('/jjzy/')
        ul = soup.first('div',{'class':'nav'})
        channelList =[]
        if ul!=None:
            ahrefs = ul.findAll('a')
            for ahref in ahrefs:
                obj={}
                if ahref.get('href')=="/" or ahref.text=='在线视频' or ahref.text=='首页':
                    continue
                obj['name']=ahref.text
                obj['url']=ahref.get('href')
                obj['baseurl']=baseurl
                obj['updateTime']=datetime.datetime.now()
                obj['pic']=''
                obj['rate']=1.2
                obj['channel']="99ziyuan"+ahref.text
                obj['showType']=3
                obj['channelType']='normal'
                channelList.append(obj)
        return channelList
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        div = soup.first("ul", {"class": "videoContent"})
        if div!=None:
            ahrefs = div.findAll('a',{"class":"videoName"})
            for ahref in ahrefs:
                obj = {}
                mp4Url = self.parseDomVideo(ahref.get("href"))
                if mp4Url == None:
                    print '没有mp4 文件:', ahref.get("href")
                    continue
                obj['url'] = mp4Url['mp4']
                obj['pic'] = mp4Url['pic']
                obj['name'] = ahref.text
                print obj['name'],obj['url'],obj['pic']

                videourl = urlparse(obj['url'])
                obj['path'] = "tzzy_"+videourl.path
                obj['updateTime'] = datetime.datetime.now()
                obj['channel'] = channel
                dataList.append(obj)
            dbVPN = db.DbVPN()
            ops = db_ops.DbOps(dbVPN)
            for obj in dataList:
                ops.inertVideo(obj,"normal",baseurl)
    
            print '99tzzy13 video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
            dbVPN.commit()
            dbVPN.close()

    def parseDomVideo(self, url):
        header = {'User-Agent':
                  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": url}
        obj = {}
        try:
            soup = self.fetchUrl(url, header)
            playtool = soup.first("div",{'class':'play-wapper'})
            if playtool!=None:
                obj['pic']="https:"+playtool.first('img').get('src')
                ahrefs = playtool.findAll('a')
                for ahref in ahrefs:
                    match = regVideo.search(ahref.text)
                    if match!=None:
                        videoUrl =match.group(1)
                        obj['mp4']= "%s%s%s"%("http:",videoUrl,'m3u8')
                        return obj
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
