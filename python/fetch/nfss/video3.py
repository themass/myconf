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
        print 'nfss user video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url = item['url']
                if i!=1:
                    url= "/%s%s%s"%(item['url'].replace(".html","page/"),i,".html")
                print url
                con = self.videoParse(item['channel'], url,item['userId'])
                print '解析完成 ', item['channel'], ' ---', i, '页'
                if con==False:
                    print '没有数据了啊-======页数',i,'---',item['name'],item['url']
                    break
    def videoChannel(self):
        ahrefs = self.header2()
        channelList = []
        for ahref in ahrefs:
            obj={}
            obj['name']=ahref.text
            obj['url']=ahref.get('href')
            obj['baseurl']=baseurl3
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1.2
            obj['channel']='nfss_all'
            obj['userId']="nfss_asy3333"+ahref.text
            obj['showType']=3
            obj['channelType']='normal'
            channelList.append(obj)
        return channelList
    def videoParse(self, channel, url,userId):
        dataList = []
        soup = self.fetchUrlWithBase(baseurl3+url,header2)
        div = soup.first("div", {"class": "hy-video-list cleafix"})
        if div!=None:
            lis = div.findAll("div",{"class":"col-md-2 col-sm-3 col-xs-4"})
            if len(lis)==0:
                return False
            for li in lis:
                #name,pic,url,userId,rate,updateTime,path
                ahref = li.first('a')
                obj = {}
                mp4Url = self.parseDomVideo(ahref.get("href"))
                if mp4Url == None:
                    print '没有mp4 文件:', ahref.get("href")
                    continue
                obj['url'] = mp4Url
                obj['pic'] = ahref.get("style").replace("background: url(","").replace(") no-repeat; background-size: 100% 100%;","")
                obj['name'] = ahref.get("title")
    
                videourl = urlparse(obj['url'])
                obj['path'] = "asy3333_"+videourl.path
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

        print 'nfss video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
        if len(dataList)==0:
            return False
        return True
    def parseDomVideo(self, url):
        try:
            Id = url.replace("/index.php/vod/detail/id/","").replace(".html","")
            url = "/index.php/vod/play/id/%s/sid/1/nid/1.html"%(Id)
            soup = self.fetchUrlWithBase(baseurl3+url, header2)
            adiv = soup.first("div",{"class":"bofang_box"})
            if adiv!=None:
                script = adiv.first('script')
                if script!=None:
                    text = unquote(str(script.text))
                    texts = text.split(",")
                    for item in texts:
                        match = regVideo.search(item)
                        if match!=None:
                            videoUrl =match.group(1).replace("\/","/")
                            mp4 = "%s%s%s"%("http",videoUrl,'m3u8')
                            return mp4
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

