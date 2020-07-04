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
        chs  = self.videoChannel()
        for ch in chs:
            ops.inertVideoChannel(ch)
        print ' channel ok; len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for ch in chs:
            for i in range(1, maxVideoPage):
                url= ch['url']
                url = "%s/page/%s.html"%(ch['url'].replace(".html",""),i)
                con = self.videoParse(ch['channel'], url)
                if con==False:
                    print '没有数据了啊-======页数',i,'---',ch['name'],ch['url']
                    break
                print '解析完成 ', ch['channel'], ' ---', i, '页'
    def videoChannel(self):
        channelList = []
        ahrefs = self.header()
        for ahref in ahrefs:
            obj={}
            obj['name']=ahref.text
            obj['url']=ahref.get('href')
            obj['baseurl']=baseurl
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1.2
            obj['channel']=obj['name']
            obj['showType']=3
            obj['channelType']='movie'
            channelList.append(obj)
#         channelList.reverse()
        return  channelList
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        lis = soup.findAll("li", {"class": "col-md-6 col-sm-4 col-xs-3"})
        if len(lis)==0:
            return False
        for li in lis:
            ahref = li.first('a')
            if ahref!=None:
                mp4Url  = self.parseDomVideo(ahref.get("href"))
                if mp4Url==None:
                    continue
                if mp4Url.count('.html')!=0 :
                    print mp4Url,"爱奇艺，忽略"
                    continue
                obj = {}
                obj['url'] = mp4Url
                obj['pic'] = baseurl+ahref.get('data-original')
                obj['name'] = ahref.get("title")
                obj['path'] = "nanguayingshi_%s%s%s"%(channel,"-",obj['name'])
                if mp4Url.count("m3u8")==0 and mp4Url.count("mp4")==0:
                    obj['videoType'] = "webview"
                else:
                    obj['videoType'] = "normal"
                print obj['videoType'],obj['name'],mp4Url,obj['pic']
                obj['updateTime'] = datetime.datetime.now()
                obj['channel'] = channel
                obj['baseurl'] = baseurl
                dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,obj['videoType'],baseurl)

        print 'nanguayingshi video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
        return True
    def parseDomVideo(self, url):
        try:
            Id = url.replace("/index.php/vod/detail/id/","").replace(".html","")
            url = "/index.php/vod/play/id/%s/sid/1/nid/1.html"%(Id)
            soup = self.fetchUrl(url)
            div   = soup.first("div",{"class":"stui-player__video clearfix"})
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
            
            print url,'没有mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

