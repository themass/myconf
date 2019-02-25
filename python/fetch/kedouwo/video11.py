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
#         for item in chs:
#             ops.inertVideoChannel(item)
        print '青青草 video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url= item['url']
                if i!=1:
                    url= "%s%s%s"%(item['url'].replace('.html','-'),i,".html")
                self.videoParse(item['channel'], url,item['url'])
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        ahrefs = self.header11()
        channelList =[]
        for ahref in ahrefs:
            obj={}
            obj['name']=ahref.text
            obj['url']=ahref.get('href')
            obj['baseurl']=baseurl11 
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=0.7
            obj['channel']='青青草'+ahref.text
            obj['showType']=3
            obj['channelType']='qqc_all'
            channelList.append(obj)
        return channelList
    def videoParse(self, channel, url,channelurl):
        dataList = []
        soup = self.fetchUrl(baseurl11+url,header8)
        div = soup.first("div",{"class":'box movie_list'})
        if div!=None:
            lis = div.findAll("li")
            for li in lis:
                ahref = li.first('a')
                if ahref != None:
                    obj = {}
                    mp4Url = self.parseDomVideo(ahref.get("href"),channelurl)
                    if mp4Url == None:
                        print '没有mp4 文件:', ahref.get("href")
                        continue
                    obj['url'] = mp4Url
                    img = ahref.first("img")
                    obj['pic'] =img.get("src")
                    obj['name'] = ahref.first("h3").text.replace(".mp4","")
                    videourl = urlparse(obj['url'])
                    obj['path'] = "qqc"+videourl.path
                    obj['updateTime'] = datetime.datetime.now()
                    if mp4Url.count("m3u8")==0 and mp4Url.count("mp4")==0:
                        obj['videoType'] = "webview"
                    else:
                        obj['videoType'] = "normal"
                    obj['channel'] = channel
                    obj['baseurl'] = baseurl11
                    print obj['videoType'],obj['name'],obj['url'],obj['pic']
                    dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,obj['videoType'],baseurl)

        print 'duotv video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url,channelurl):
      
        try: 
            channelurl = channelurl.replace(".html","")
            url = url.replace(channelurl,"").replace("/Category/","").replace("Detailed/", "").replace(".html","")
            url= "%s%s%s"%("/Category/Watch-online_",url,"-1-1.html")
            soup = self.fetchUrl(baseurl11+url,header8)
            scripts = soup.findAll("script")
            for script in scripts:
                if script.get("src")!=None and script.get("src").count("/upload/playdata")==1:
                    text = unquote(str(self.fetchContentUrl(baseurl11+script.get("src"),header8)))
                    texts = text.split("$")
                    for item in texts:
                        match = regVideoM3.search(item)
                        if match!=None:
                            videoUrl =match.group(1)
                            return "%s%s%s"%("http",videoUrl,'m3u8')
#                 shell = "%s %s"%("wget ",aherf)
#                 ret = os.popen(shell).read()
#                 print ret
#                 if len(ret)>0:
#                     for item in ret:
#                         item = unquote(str(item))
#                         match = regVideo.search(item)
#                         if match!=None:
#                             return 'http'+match.group(1)
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
