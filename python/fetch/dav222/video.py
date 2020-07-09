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
        print '444dav user video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            start = 1
            if item['name'].count('91视频')>0:
                start = 20
            for i in range(start, maxVideoPage):
                url= item['url']
                if i!=1:
                    url = "%sindex_%s.html"%(item['url'],i)
                print url
                con = self.videoParse(item['channel'], url,item['userId'])
                if con==False:
                    print '没有数据了啊-======页数',i,'---',item['name'],item['url']
                    break
                print '解析完成 ', item['channel'], ' ---', i, '页'
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
            obj['userId']="8x8x"+ahref.text
            obj['showType']=3
            obj['channelType']='normal'
            channelList.append(obj)
        return channelList
    def videoParse(self, channel, url,userId):
        dataList = []
        soup = self.fetchUrl(url)
        div = soup.first("ul",{"class":"stui-vodlist clearfix"})
        if div!=None:
            lis = div.findAll("li",{"class":"col-md-6 col-sm-4 col-xs-3"})
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
                obj['pic'] = baseurl+ahref.get("data-original",'')
                obj['name'] = ahref.get('title')
    
                videourl = urlparse(obj['url'])
                obj['path'] = "444dav_"+videourl.path
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
            url = '%s%s'%(url,'index_1_1.html')
            soup = self.fetchUrl(url)
            div   = soup.first("div",{"class":"stui-player col-pd"})
            if div !=None:
                texts = unquote(div.text.replace("'",'').replace(")",'').replace(";",'').replace('"url":"','').replace('"',"").replace("\/",'/')).split(",")
                for text in texts:
                    match = videoApi.search(text)
                    if match!=None:
                        str= match.group(1)
                        return "%s%s%s"%("http",str,".m3u8")
                for text in texts:
                    match = shareVideo.search(text)
                    if match!=None:
                        return text
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

