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
#         for item in chs:
#             ops.inertVideoChannel(item)
        print 'hq video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url = item['url']
                if i!=1:
                    url= "%s%s%s"%(item['url'].replace(".html","-pg-"),i,".html")
                print url
                self.videoParse(item['channel'], url,item['baseurl'])
                print '解析完成 ', item['baseurl'],item['channel'], ' ---', i, '页'
                time.sleep(1)
    def videoChannel(self):
        channelList = []
        ahrefs = self.header("header.html")
        for ahref in ahrefs:
            obj={}
            obj['name']=ahref.get("title").replace("av","")
            obj['url']=ahref.get('href')
            obj['baseurl']=baseurl
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1.2
            obj['channel']='qh'+ahref.get("title").replace("av","")
            obj['showType']=3
            obj['channelType']='qh_all'
            channelList.append(obj)
#         ahrefs = self.header("header2.html")
#         for ahref in ahrefs:
#             obj={}
#             obj['name']=ahref.get("title").replace("av","")
#             obj['url']=ahref.get('href')
#             obj['baseurl']=baseurl2
#             obj['updateTime']=datetime.datetime.now()
#             obj['pic']=''
#             obj['rate']=1.2
#             obj['channel']='qh'+ahref.get("title").replace("av","")
#             obj['showType']=3
#             obj['channelType']='qh_all'
#             channelList.append(obj)
        ahrefs = self.header("header3.html")
        for ahref in ahrefs:
            obj={}
            obj['name']=ahref.get("title").replace("av","")
            obj['url']=ahref.get('href')
            obj['baseurl']=baseurl3
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1.2
            obj['channel']='qh'+ahref.get("title").replace("av","")
            obj['showType']=3
            obj['channelType']='qh_all'
            channelList.append(obj)
        return channelList
    def videoParse(self, channel, url,base):
        dataList = []
        print base+url
        soup = self.fetchUrlWithBase(base+url)
        ul = soup.first("ul",{"class":"videos"})
        if ul!=None:
            metas = ul.findAll("li")
            for meta in metas:
                obj = {}
                ahref = meta.first("a")
                mp4Url = self.parseDomVideo(base,ahref.get("href"))
                if mp4Url == None:
                    print '没有mp4 文件:', ahref.get("href")
                    continue
                obj['url'] = "http://qsv.jxckplayer.xyz/yun/?vid="+mp4Url
                obj['pic'] = meta.first('img').get("src")
                obj['name'] = meta.first('img').get("alt")
    
                videourl = urlparse(mp4Url)
                obj['path'] = 'qh_'+videourl.path
                obj['updateTime'] = datetime.datetime.now()
                obj['channel'] = channel
                obj['videoType'] = "webview"
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
            soup = self.fetchUrlWithBase(base+url, header)
            div = soup.first("div",{'class':'players'})
            if div!=None:
                script = div.first('script')
                if script!=None:
                    text = unquote(script.text.replace("\"","").replace("\/","/"))
                    texts = text.split(",")
                    for item in texts:
                        match = regVideo.search(item)
                        if match!=None:
                            videoUrl =match.group(1)
                            return "%s%s%s"%("http",videoUrl,'m3u8')
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
