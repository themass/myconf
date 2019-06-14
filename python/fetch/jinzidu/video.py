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
        print 'jinzidu video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url = item['url']
                if i!=1:
                    url= "%s%s%s%s"%(item['url'],"index",i,".html")
                print url
                self.videoParse(item['channel'], url,item['baseurl'])
                print '解析完成 ', item['baseurl'],item['channel'], ' ---', i, '页'
                time.sleep(1)
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
            obj['channel']=obj['name']
            obj['showType']=3
            obj['channelType']='movie'
            channelList.append(obj)
        ahrefs = self.header("header2.html")
        for ahref in ahrefs:
            obj={}
            obj['name']=ahref.text
            obj['url']=ahref.get('href')
            obj['baseurl']=baseurl
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1
            obj['channel']='日韩午夜'
            obj['showType']=3
            obj['channelType']='shanji'
            channelList.append(obj)
        channelList.reverse()
        return channelList
    def videoParse(self, channel, url,base):
        dataList = []
        soup = self.fetchUrl(url)
        metas = soup.findAll("li",{"class":"col-md-6 col-sm-4 col-xs-3"})
        for meta in metas:
            obj = {}
            ahref = meta.first("a")
            mp4Url = self.parseDomVideo(base,ahref.get("href"))
            if mp4Url == None:
                print '没有mp4 文件:', ahref.get("href")
                continue
            obj['url'] = mp4Url['url']
            obj['pic'] = ahref.get("data-original")
            obj['name'] = ahref.get("title")

            videourl = urlparse(mp4Url['url'])
            obj['path'] = 'jinzidu_'+videourl.path
            obj['updateTime'] = datetime.datetime.now()
            obj['channel'] = channel
            obj['videoType'] = mp4Url['type']
            obj['baseurl'] = baseurl
            print obj['name'],obj['videoType'],obj['url'],obj['pic']
            dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,obj['videoType'],baseurl)

        print 'qh video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, base,url):
        try:
            url = "%s%s"%(url,"0-1.html")
            soup = self.fetchUrlWithBase(base+url, header)
            div = soup.first("iframe")
            if div!=None and div.get("src")!=None:
                if div.get("src").count("//pp.aism.cc/kb.php?vid=")!=0:
                    item = div.get("src").replace("http://pp.aism.cc/kb.php?vid=","").replace("//pp.aism.cc/kb.php?vid=","").replace("~m3u8","")
                    match = regVideo.search(item)
                    videoItem = {}
                    if match!=None:
                        videoUrl =match.group(1)
                        videoItem['type']='normal'
                        videoItem['url']="%s%s%s"%("http",videoUrl,'m3u8')

                        return videoItem
                    else:
                        videoItem['type']='webview'
                        videoItem['url']=div.get("src")
                        return videoItem
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
