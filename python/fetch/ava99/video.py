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
        print 'bt2n video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url = item['url']
                if i!=1:
                    url= "%s%s%s"%(item['url'].replace("1.html",""),i,".html")
                print url
                self.videoParse(item['channel'], url,item['baseurl'])
                print '解析完成 ', item['baseurl'],item['channel'], ' ---', i, '页'
    def videoChannel(self):
        channelList = []
        ahrefs = self.header("header.html")
        for ahref in ahrefs:
            obj={}
            obj['name']=ahref.text
            obj['url']=ahref.get('href')
            obj['baseurl']=baseurl
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1
            obj['channel']='ava99'+ahref.text
            obj['showType']=3
            obj['channelType']='ava99_all'
            channelList.append(obj)
        channelList.reverse()
        return channelList
    def videoParse(self, channel, url,base):
        dataList = []
        soup = self.fetchUrl(url)
        metas = soup.findAll("li",{"class":"col-md-2 col-sm-3 col-xs-4"})
        for meta in metas:
            obj = {}
            ahref = meta.first("a")
            if ahref!=None:
                print ahref.get("href")
                match = videoId.search(ahref.get("href"))
                if match!=None:
                    Id= match.group(1)
                    mp4Url  = self.parseDomVideo(Id)
                    if mp4Url == None:
                        print '没有mp4 文件:', ahref.get("href")
                        continue
                    obj['url'] = mp4Url
                    obj['pic'] = ahref.get("data-original")
                    pname = ahref.get("title")
                    obj['name'] = pname
        
                    videourl = urlparse(mp4Url)
                    obj['path'] = 'ava99_'+videourl.path
                    obj['updateTime'] = datetime.datetime.now()
                    obj['channel'] = channel
                    obj['videoType'] = "normal"
                    obj['baseurl'] = baseurl
                    print obj['name'],obj['videoType'],obj['url'],obj['pic']
                    dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,obj['videoType'],baseurl)
#             ops.renameVideo(obj)
 
        print 'qh video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, id):
        try: 
            soup = self.fetchUrl("/%s%s%s"%("vod-play-id-",id,"-src-1-num-1.html"), header)
            div = soup.first("div",{'class':'container'})
            if div!=None:
                scripts = div.findAll('script')
                for script in scripts:
                        text = unquote(script.text)
                        texts = text.split("$")
                        for item in texts:
                            match = regVideo.search(item)
                            if match!=None:
                                videoUrl =match.group(1)
                                return "%s%s%s"%("http",videoUrl,'.m3u8')
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
