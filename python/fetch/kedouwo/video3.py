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
        print 'asy007 user video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url= item['url']
                if i!=1:
                    url= "%s%s%s"%(item['url'].replace('.html',"/page/"),i,".html")
                print url
                self.videoParse(item['channel'], url,item['userId'])
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        ahrefs = self.header3()
        channelList = []
        for ahref in ahrefs:
            obj={}
            obj['name']=ahref.text
            obj['url']=ahref.get('href')
            obj['baseurl']=baseurl3
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1.2
            obj['channel']='经典蝌蚪窝2'
            obj['userId']="kd2"+ahref.text
            obj['showType']=3
            obj['channelType']='normal'
            channelList.append(obj)
        return channelList
    def videoParse(self, channel, url,userId):
        dataList = []
        soup = self.fetchUrl(baseurl3+url,header3)
        div = soup.first("div", {"class": "box-video-list"})
        if div!=None:
            lis = div.findAll("li",{"class":"col-md-2 col-sm-3 col-xs-4 "})
            for li in lis:
                #name,pic,url,userId,rate,updateTime,path
                ahref = li.first("a")
                obj = {}
                mp4Url = self.parseDomVideo(ahref.get("href"))
                if mp4Url == None:
                    print '没有mp4 文件:', ahref.get("href")
                    continue
                obj['url'] = mp4Url
                obj['pic'] = ahref.get("data-original")
                obj['name'] = li.first("h5").text
    
                videourl = urlparse(obj['url'])
                obj['path'] = "asy1000"+videourl.path
                obj['rate'] = 1.2
                obj['updateTime'] = datetime.datetime.now()
                obj['userId'] = userId
                obj['baseUrl'] = baseurl3
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

        print 'v88hd video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
        time.sleep(0.5)

    def parseDomVideo(self, url):
        try:
            match = videoId3.search(url)
            if match!=None:
                videoId = match.group(1)
                videoUrlId = "/index.php/vod/play/id/%s/sid/1/nid/1.html"%(videoId)
                soup = self.fetchUrl(baseurl3+videoUrlId, header3)
                DIV    = soup.first("div",{"class":"bofang_box"})
                if DIV  !=None:
                        text = unquote(str(DIV.text)).replace("\/", "/")
                        texts = text.split(",")
                        for item in texts:
                            match = regVideoM3.search(item)
                            if match!=None:
                                videoUrl =match.group(1)
                                return "%s%s%s"%("http",videoUrl,'m3u8')
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

