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
        print 'shixunziyuan user video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url = item['url']
                if i!=1:
                    url= "/%s%s%s"%(item['url'].replace(".html","/page/"),i,".html")
                print url
                count = self.videoParse(url, url,item['userId'])
                if count==0:
                    break
                print '解析完成 ', url, ' ---', i, '页'
    def videoChannel(self):
        ahrefs = self.header7()
        channelList = []
        for ahref in ahrefs:
            obj={}
            obj['name']=ahref.text
            obj['url']=ahref.get('href')
            obj['baseurl']=baseurl7
            obj['updateTime']=datetime.datetime.now()
            obj['pic']='' 
            obj['rate']=1.2
            obj['channel']='8x8x拔插'
            obj['userId']='baoyu_'+ahref.text
            obj['showType']=3
            obj['channelType']='normal'
            channelList.append(obj)
        return channelList
    def videoParse(self, channel, url,userId):
        dataList = []
        soup = self.fetchUrlWithBase(baseurl7+url, header3)
        lis = soup.findAll("li",{"class":"col-md-6 col-sm-4 col-xs-2"})
        for li in lis:
            #name,pic,url,userId,rate,updateTime,path
            ahref = li.first("a")
            if ahref!=None:
                obj = {}
                mp4Url = self.parseDomVideo(ahref.get('href'))
                if mp4Url == None:
                    print '没有mp4 文件:', ahref.get("href")
                    continue
                obj['url'] = mp4Url
                obj['pic'] = ahref.get('data-original')
                obj['name'] = ahref.get("title")
    
                videourl = urlparse(obj['url'])
                obj['path'] = "baoyu_"+videourl.path
                obj['rate'] = 1.2
                obj['updateTime'] = datetime.datetime.now()
                obj['userId'] = userId
                obj['baseUrl'] = baseurl7
                obj['showType'] = 3
                if obj['url'].count("m3u8")==0 and obj['url'].count("mp4")==0:
                    obj['videoType'] = "webview"
                else:
                    obj['videoType'] = "normal"
                print obj['videoType'],obj['name'],mp4Url,obj['pic']
                dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideoUserItem(obj)

        print 'shixunziyuan video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
        
        return len(dataList)
    def parseDomVideo(self, url):
        try:
            soup = self.fetchUrlWithBase(baseurl7+url, header7)
            div = soup.first("div", {"class":"stui-player__video embed-responsive embed-responsive-16by9 clearfix"})
            if div !=None:
                text = unquote(div.text)
                texts = text.split(",")
                for item in texts:
                    match = regVideo7.search(item)
                    if match!=None:
                        videoUrl =match.group(1)
                        return "%s%s%s"%("https://z.weilekangnet.com:59666",videoUrl.replace("\/","/"),'m3u8')
 
 #if url.count("https://imgcdn1.weilekangnet.com:59666")==0:
#                 print url,'没有mp4'
#                 return None
#             return url.replace("https://imgcdn1.weilekangnet.com:59666","https://bycdn0l.weilekangnet.com:59666").replace("pic.jpg","index.m3u8")
        except Exception as e:
            print common.format_exception(e)
            return None

