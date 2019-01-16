#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from urllib import unquote
import time
from fetch.profile import *
from common import db_ops
class VideoUserParse(BaseParse):

    def __init__(self):
        pass

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        chs = self.videoChannel()
        for item in chs:
            ops.inertVideoUser(item)
        print 'aotu user video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url= item['url']
                url = "%s%s%s"%(url, str(i),".html")
                print url
                self.videoParse(item['channel'], url,item['userId'])
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        channelList = []
        for name,url in video_channels.items():
            obj={}
            obj['name']=name
            obj['url']=url
            obj['baseurl']=baseurl
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1.2
            obj['channel']='1024clsmik_all'
            obj['userId']='1024clsmik_'+name
            obj['showType']=3
            obj['channelType']='normal'
            channelList.append(obj)
        return channelList
    def videoParse(self, channel, url,userId):
        dataList = []
        soup = self.fetchUrl(url)
        trs = soup.findAll("tr",{"class":"tr3 t_one"})
        for tr in trs:
            h3 = tr.first("h3")
            if h3!=None:
                ahref = h3.first("a")
                if ahref != None and ahref.get("href").count("html_data")>0:
                    obj = {}
                    mp4Url = self.parseDomVideo(ahref.get("href"))
                    if mp4Url == None:
                        print '没有mp4 文件:', ahref.get("href")
                        continue
                    obj['url'] = mp4Url
                    obj['pic'] = ""
                    obj['name'] = h3.text
        
                    videourl = urlparse(obj['url'])
                    obj['path'] = "aotu"+videourl.path
                    obj['rate'] = 1.2
                    obj['updateTime'] = datetime.datetime.now()
                    obj['userId'] = userId
                    obj['baseUrl'] = baseurl
                    obj['showType'] = 3
                    if mp4Url.count("m3u8")==0 and mp4Url.count("mp4")==0:
                        obj['videoType'] = "webview"
                    else:
                        obj['videoType'] = "normal"
                    print obj['videoType'],obj['name'],mp4Url,obj['pic']
                    dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideoUserItem(obj)

        print 'clsmik video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
        try:
            soup = self.fetchUrl(url)
            iframe = soup.first("iframe")
            if iframe !=None:
                v = iframe.get("src").replace("&#46;",".")
                match = video_iframe.search(v)
                if match!=None:
                    id = v.replace("https://baiduyunbo.com/?id=","")
                    return video_m3u8%(id)
                else:
                    soup = self.fetchUrl(v)
                    scripts = soup.findAll("script")
                    for script in scripts:
                        match = video_mp4.search(script.text)
                        if match!=None:
                            return "%s%s%s"%("http",match.group(1),"mp4")
                            
            print url,'没有找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

