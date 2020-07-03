#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from urllib import unquote
import time
from fetch.profile import *
class VideoUserParse(BaseParse):

    def __init__(self):
        pass

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        chs = self.videoChannel()
        for item in chs:
            ops.inertVideoUser(item)
        print 'eufram user video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url= item['url']
                url = "%s%s.html"%(item['url'].replace("1.html",""),i)
                print url
                con = self.videoParse(item['channel'], url,item['userId'])
                if con==False:
                    print '没有数据了啊-======页数',i,'---',item['name'],item['url']
                    break
                print '解析完成 ', item['channel'], ' ---', i, '页'
                time.sleep(2)
    def videoChannel(self):
        ahrefs = self.header()
        channelList = []
        for ahref in ahrefs:
            obj={}
            obj['name']=ahref.text
            obj['url']=ahref.get('href')
            obj['baseurl']=baseurl
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1.2
            obj['channel']='8x8x拔插'
            obj['userId']="eufram_"+ahref.text
            obj['showType']=3
            obj['channelType']='normal'
            channelList.append(obj)
        return channelList
    def videoParse(self, channel, url,userId):
        dataList = []
        soup = self.fetchUrl(url)
        div = soup.first("div",{"class":"panel-max"})
        if div!=None:
            lis = div.findAll("li")
            if len(lis)==0:
                return False
            for li in lis:
                ahref = li.first("a")
                if ahref ==None:
                    continue
                obj = {}
                mp4Url = self.parseDomVideo(ahref.get("href"))
                if mp4Url == None:
                    print '没有mp4 文件:', ahref.get("href")
                    continue
                obj['url'] = mp4Url
                img = li.first("img")
                obj['pic'] = img.get("src")
                obj['name'] = img.get("alt")
    
                videourl = urlparse(obj['url'])
                obj['path'] = "eufram_"+videourl.path
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

        print '8x8x video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
        return True
    def parseDomVideo(self, url):
        try:
            Id = url.replace("/vod-detail-id-","").replace(".html","")
            url = "/vod-play-id-%s-src-1-num-1.html"%(Id)
            soup = self.fetchUrl(url)
            div   = soup.first("div",{"id":"cms_player"})
            if div !=None:
                texts = unquote(div.text).split(",")
                for text in texts:
                    match = videoApi.search(text)
                    if match!=None:
                        str= match.group(1)
                        return "%s%s%s"%("http",str,".m3u8")
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

